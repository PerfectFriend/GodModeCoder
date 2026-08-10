# Electrician-thief prototype — verified run & integration (2026-08-05)

Working prototype for the "thief disguised as electrician" cable-theft brief.
Location: `C:\Users\tomas\video-surveillance\` (sibling of surveillance.py core).

## Files

| File | Role |
|---|---|
| `electrician_detector.py` | `analyze_frame(frame, detections)` → list of `electrician_thief` alerts; `detect_hi_vis`, `find_pole`, `draw_alerts` |
| `actuator.py` | `Actuator(cfg)` with modes `esp32` / `webhook` / `sim`; `.trigger(reason, duration)` |
| `demo_prototype.py` | End-to-end: `--source synth\|file\|rtsp`, `--actuator sim\|esp32\|webhook`, `--direct`, `--chat-id`, `--no-telegram`, `--no-act` |
| `docs/esp32_alarm.ino` | ESP32 firmware: GPIO2→floodlight relay, GPIO4→siren relay, `/on` `/off` `/status` |
| `synth_thief_frame()` (in demo) | Synthetic test frame: dark scene, person, yellow helmet+vest, УКН pole to the cable |

## Detection logic (form-based, no fine-tune)

- Cable zone = top band of frame, default `y ≤ 0.35` (cable strung 4–5 m up).
- Pole: `MORPH_OPEN` with `(1,15)` kernel → Otsu → contours; accept aspect ≥ 4, height ≥ 25%,
  width 2–24 px, top inside cable zone. Confidence 0.89 achieved on synthetic test.
- Helmet/vest: HSV yellow/orange masks; helmet head-frac > 0.08, vest torso-frac > 0.05.
  Hi-vis fraction on synthetic vest measured 78%.
- Alert fires on `pole_found AND pole_in_cable`; helmet/vest add +0.15 each to confidence.

## Verified end-to-end run (real output)

```
🚨 ОБНАРУЖЕН ВОР-ЭЛЕКТРИК: alert_2026-08-05_02-02-11.jpg (conf=0.89)
📸 Фото + текст отправлены в Telegram          (chat 143293811)
🚨 SIM-АКТУАТОР: прожектор ВКЛ + сирена ВКЛ на 30с — причина: вор-электрик (conf=0.89)
```

Command: `python demo_prototype.py --source synth --direct --chat-id 143293811`
(`--direct` injects person bbox `(280,235,360,460)` because YOLO does not detect the
primitive drawn silhouette; YOLO DOES detect real persons, verified on `test-person.jpg`:
4 persons conf 0.62–0.89.)

## Pitfalls hit

1. `DetectorWrapper` lives in `demo_prototype.py` (bottom), NOT in `electrician_detector.py` —
   first run failed with `AttributeError` until call was changed to the local class.
2. YOLO on synthetic frames → zero person detections. Real footage or `--direct` needed.
3. Windows `tasklist` cp866 decoding — fixed in `pulse.py` via `decode("cp866", errors="ignore")`
   and PowerShell `Get-CimInstance` for `.py` processes.
4. Telegram silently skipped when `telegram_channel: null` — pass `--chat-id` or set config.

## Actuator integration

- `sim` mode: logs `logs/actuator_events.jsonl` (JSON lines: mode, reason, duration, ok, ts).
- `esp32` mode: GET `{base}{on_path}` → sleep duration → GET `{base}{off_path}`.
- For a real demo: flash `docs/esp32_alarm.ino` (set SSID/password), run with
  `--actuator esp32` and `base_url` in config `actuator:` section.

## Note on YOLO confidence on real vs synthetic

On the ultralytics `bus.jpg` asset: 4 persons at 0.62–0.89 conf — the core pipeline
works against real imagery. The electrician detector layers on top of YOLO person boxes;
on real site footage the pole heuristic should be validated against actual УКН footage
before production (day + night/IR).
