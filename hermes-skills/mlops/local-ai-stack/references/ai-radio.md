# AI-radio «Мастер-ФМ» — architecture (in progress 2026-08)

Local AI radio: a DJ agent that mixes cached audio (music, news, ads, jingles, audiobooks)
into a continuous stream. All content is generated locally — ACE-Step (music) + Voicebox
(voice: news/ads/jingles) — no cloud traffic during broadcast.

## Directory layout
```
C:\Users\tomas\ai-radio\
├── config.yaml            # styles, news cats, jingle themes, schedule, dj voice profile
├── cache\
│   ├── music\<style>\     # rock, jazz, electronic, ambient, chiptune, classical
│   ├── news\<cat>\        # world, tech, sport, local  (voicebox WAVs)
│   ├── ads\               # рекламные ролики (voicebox)
│   ├── jingles\<theme>\   # morning, traffic, holidays, funny
│   └── audiobooks\
├── playlist.txt           # ffmpeg concat list (regenerated per broadcast)
└── scripts\
    ├── gen_music.py       # ACE-Step → cache/music/<style>/ (see acestep-cpu.md)
    ├── gen_voice_content.py  # Voicebox → news/ads/jingles (uses voicebox_tts.py)
    └── dj.py              # stream server
```

## Broadcast chain (proven pattern: ffmpeg → ring buffer → HTTP)
1. **Playlist**: `build_playlist()` picks one file per block from each cache folder,
   alternating music styles, inserting jingles every N tracks, news/ads per schedule,
   audiobooks at night hours. Rules live in `config.yaml: radio.schedule`.
2. **Mix**: one long-lived ffmpeg process reads the concat list forever and encodes to
   a continuous MP3 stream on stdout:
   ```
   ffmpeg -stream_loop -1 -f concat -safe 0 -i playlist.txt -ar 44100 -b:a 128k -f mp3 pipe:1
   ```
   (concat list format: `file 'path'` lines; escape `'` by doubling.)
3. **Ring buffer**: a thread pumps ffmpeg stdout into a bytearray capped at
   `RING_SECONDS * sample_rate * channels * 2` bytes (~5 s). Keeps the last seconds so a
   listener joining mid-stream doesn't start in silence.
4. **HTTP**: raw socket server on `0.0.0.0:8090/radio`; each connection gets
   `Content-Type: audio/mpeg` + the buffer snapshot, then live chunks while `snap != last`.
   Simple, dependency-free, playable in a browser / VLC / phone on LAN.

## Voice content generation
`gen_voice_content.py` holds topic→phrases dicts (news/ads/jingles), synthesizes each via the
same `voicebox_tts.py` command wrapper (see SKILL.md "Wire Voicebox into Hermes"), skips
files that already exist (idempotent), sleeps 1 s between calls. ~30 s per clip on CPU.

## Notes / gotchas
- Keep voice clips short (≤ ~1000 chars) — CPU synthesis is slow; long texts risk the 300 s
  command-provider timeout.
- ffmpeg 8.x `-stream_loop -1` on concat input is the reliable "infinite playlist" trick.
- The DJ script is a long-lived daemon — start via background terminal, not cron-per-minute.
