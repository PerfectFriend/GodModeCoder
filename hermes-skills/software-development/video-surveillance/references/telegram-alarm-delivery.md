# Telegram alarm delivery cycle — VERIFIED live 2026-08-06

Full alarm UX validated against the live stack (Tuya plug + Telegram bot + HLS camera):
alarm → plug ON + `sendPhoto` (caption + inline cancel button) → every **2 s**
`editMessageMedia` refreshes the SAME message with a fresh frame → "cancel" callback →
plug OFF + chat cleanup. Final client decision 2026-08-06: **photo-refresh only, no
stream button, single 🚨 Отмена тревоги button**.

## The one-liner summary

`sendPhoto` and `editMessageMedia` have **DIFFERENT multipart formats** — do not reuse the
same `files=` dict:

```python
# sendPhoto: field name must be "photo"; filename is second tuple element
files = {"photo": ("frame.jpg", frame_bytes, "image/jpeg")}

# editMessageMedia: files-dict KEY must equal the attach:// name exactly
files = {"frame.jpg": frame_bytes}
media = {"type": "photo", "media": "attach://frame.jpg", "caption": caption}
```

- Wrong key for editMessageMedia → HTTP 400 `Bad Request: can't parse InputMedia: media not
  found` (the device IS alive — the multipart filename never matched `attach://`).
- `editMessageMedia` requires `chat_id` + `message_id` + `media` (JSON string) in `data=`,
  file bytes in `files=` — all in the same POST.
- Verified working combo (requests lib): sendPhoto uses tuple form; editMessageMedia uses
  bare-bytes keyed by filename. Both confirmed by round-trip (edit succeeded → True).

## Full cycle recipe

```python
# 1. ALARM
plug_set(True)                                   # tinytuya, protocol 3.4, fresh Device
frame = grab_frame()                             # HLS/RTSP/MJPEG via cv2, jpg bytes
res = tg("sendPhoto", files={"photo": ("frame.jpg", frame_bytes, "image/jpeg")},
         data={"chat_id": CHAT, "caption": desc,
               "reply_markup": json.dumps({"inline_keyboard": [[
                   {"text": "🚨 Отмена тревоги", "callback_data": "cancel_alarm"},  # callback
               ]]})})
msg_id = res["message_id"]; known_msg_ids.add(msg_id)

# 2. UPDATE LOOP (thread): every 2 s
fname = f"frame_{int(time.time())}.jpg"        # UNIQUE name - Telegram caches by filename!
tg("editMessageMedia",
   files={fname: fresh_bytes},
   data={"chat_id": CHAT, "message_id": msg_id,
         "media": json.dumps({"type": "photo", "media": f"attach://{fname}",
                              "caption": f"АЛАРМ АКТИВЕН {time}"})})
# editMessageMedia DROPS the keyboard -> MUST re-apply right after, or cancel dies:
tg("editMessageReplyMarkup", data={"chat_id": CHAT, "message_id": msg_id,
    "reply_markup": json.dumps({"inline_keyboard": [[
        {"text": "🚨 Отмена тревоги", "callback_data": "cancel_alarm"}]]})})

# 3. BUTTON HANDLER (long-poll getUpdates thread, offset tracking)
#    callback_query.data == "cancel_alarm":
plug_set(False)                                  # OFF
for mid in known_msg_ids: tg("deleteMessage", data={...})   # chat cleanup
#    also record user message_ids from getUpdates so their messages get cleared too
```

## Pitfalls

- **`editMessageMedia` caches the attach by FILENAME — use a unique name per update.**
  Observed live 2026-08-06: refreshing with a constant `frame.jpg` made Telegram keep
  showing the FIRST image (client: "кадр остается тот же") while the camera feed was
  clearly alive (two grabs 2.5 s apart had `absdiff().mean()` ≈ 1.3 and ~8k px >10 changed
  on a 704×576 night scene). Fix: `fname = f"frame_{int(time.time())}.jpg"` on every
  refresh, matching `attach://{fname}`. Diagnostic order when "frame doesn't change":
  (1) verify camera frames actually differ (`cv2.absdiff` on consecutive grabs — a live
  scene is never pixel-identical), (2) if they differ but Telegram shows the same image,
  it's the filename cache — not a dead feed, not a broken loop.
- **`editMessageMedia` resets the inline keyboard** (buttons are not part of the media
  edit API). The cancel button disappears after the first refresh unless you follow every
  `editMessageMedia` with `editMessageReplyMarkup` carrying the SAME keyboard. Client
  explicitly flagged this mid-test: "после обновления картинки пропадает кнопка" — a lost
  cancel button means nobody can end the alarm. This is the #1 alarm-UX bug; check it in
  every refresh loop.
- **Refresh loop must read from a CONTINUOUS background capture thread — never from a
  single persistent `cv2.VideoCapture`.** Observed regression 2026-08-06: with the stream
  server's background capture thread running, every refresh frame was fresh (client:
  "кадры при обновлении были разные"); after switching to a module-global `_cap` opened
  once and read every 2 s, the feed went FROZEN — the client saw live traffic on the
  camera but every Telegram refresh showed the same image. OpenCV's HLS demuxer buffers
  frames in order, so a slow reader gets stale buffered frames, not the latest. Correct
  pattern: daemon thread `while True: cap.read() → imencode → store latest bytes under a
  lock` (reconnect on failure, 2 s sleep); the 2 s refresh loop just reads `latest()`.
  Verified: md5 of grabbed frames unique every 2 s; grab cost ~1 ms. Reopening the URL per
  frame costs ~4 s (loop degrades to ~6 s) — also wrong. Same Camera class as
  `scripts/stream_server.py`; standalone probe: `scripts/bg_capture.py`.
- **`input()` in a background/pty process hangs** (Windows/MSYS): the interactive prompt
  never receives the submitted line reliably. Design alarm scripts as non-interactive —
  `argparse --trigger` + infinite keep-alive loop, or a /alarm Telegram command — never
  `input("> ")`.
- Inline keyboard buttons: URL button (`{"text": ..., "url": ...}`) opens the browser;
  callback button (`callback_data`) must be answered with `answerCallbackQuery` (else the
  user sees a spinner) and processed via `getUpdates` with a monotonic `offset`.
- Track `known_msg_ids` in a thread-safe set (lock) — the update thread and poll thread
  both touch it.
- **Fast fresh-frame alternative: persistent ffmpeg rawvideo pipe** (when the cv2 thread
  is not an option). Spawning `ffmpeg -frames:v 1` per frame costs 3.7–5.3 s — too slow
  for a 2 s loop. Instead keep one process alive: `ffmpeg -i URL -f rawvideo -pix_fmt
  bgr24 -an pipe:1`, then `proc.stdout.read(w*h*3)` = one fresh frame in ~1 ms (verified
  md5-unique each grab). Size probe: `ffprobe -v error -select_streams v:0 -show_entries
  stream=width,height -of csv=p=0 URL` — NOTE the output puts width and height on SEPARATE
  lines; join on `,` before `split(",")` (else ValueError from `"576\n\n704"`).

## Optional live stream server (NOT part of the final UX)

The client tested a live-view option and **chose photo-refresh only** — the stream server
below stays available as an OPTIONAL add-on (e.g. a "watch live" URL button for a second
user who wants continuous viewing), not the default alarm UX.
`scripts/stream_server.py` (OpenCV capture thread + ThreadingHTTPServer):
- `/` HTML viewer page, `/stream.mjpg` multipart MJPEG (~15–20 fps), `/status` JSON.
- Listen `0.0.0.0`; give the phone the PC's LAN IP (e.g. `http://192.168.1.156:8090/`).
- Phone must be on the SAME network; Windows Firewall may need an admin rule
  (`netsh advfirewall firewall add rule ... localport=8090` — requires elevation).
- Offer it to the client first; if they prefer the 2 s photo refresh, drop the URL button
  and the stream server from the alarm message (keeps the bot message minimal).
