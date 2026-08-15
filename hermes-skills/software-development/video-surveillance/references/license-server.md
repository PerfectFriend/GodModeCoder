# CableGuard license/subscription server (2026-08-05)

Turns the product into recurring revenue. Repo: `PerfectFriend/cableguard-server`
(**private** — business tooling, don't make public). Local: `C:\Users\tomas\cableguard-server\`.

## Business model (Spain, cable-theft market)

| Item | Price |
|---|---|
| Server + router install | 500 € one-off |
| Per camera | 100 € one-off |
| Subscription (24/7 support) | 50 €/month per camera |
| 8-camera project | 400 €/month recurring |

Hardware sold at cost (no margin) — margin is in install + subscription. README must be
in the customer's language. Payment automation (Stripe/Bizum → auto-activate) is a future step;
**manual activate/block first**.

## Server (`server.py`, FastAPI + SQLite)

- `POST /api/installations` — register a client mini-PC (`device_id`, name, location);
  idempotent (dup → `already_exists`).
- `GET /api/installations` — admin list (joined with latest subscription status).
- `POST /api/subscriptions/activate` — `{installation_id, cameras, months, price_month_eur}`;
  inserts active sub with `expires_at = now + 30d*months`.
- `POST /api/subscriptions/block` — set latest sub `status='blocked'`.
- `GET /api/license/check?device_id=...` — client probe: `ok:true` only when sub exists,
  not blocked, not expired; else `{ok:false, reason: no_subscription|blocked|expired}`.
- `GET /api/health`.
- Run: `python server.py --port 8765` (uvicorn, host 0.0.0.0). DB auto-created at `license.db`.

## Client side (`license_client.py`, runs on the customer mini-PC)

- `get_device_id()` — stable per machine: Windows `getmac` MAC → `cableguard-<mac>`;
  Linux `uuid.getnode()`. Survives reboots, no user config needed.
- `check` action: one probe, exit 0/1 (used as a guard before starting surveillance).
- `watch` action: poll every N sec; on block/expiry print + optional Telegram alert
  (`--tg-token/--tg-chat`).
- **Graceful degradation**: server unreachable → `{ok:false, reason:"server_unreachable"}`
  (surveillance must NOT hard-crash; decide policy: fail-open or fail-closed).

## Canonical test (`test_license.py`)

`python test_license.py` — the repo's canonical test command. Starts uvicorn on a free port
with a **temp DB** (`tempfile.mkdtemp` + `server.DB_PATH` override BEFORE `init_db()`),
drives the full lifecycle over real HTTP: health → register → check(no_sub) → activate(8 cams)
→ check(ok) → block → check(blocked) → unknown device → list → duplicate → client
device_id format → client active → client blocked → client unreachable. 14 checks, exits 0/1.

**Lesson from the session**: the system (Hermes) demands *fresh passing verification evidence*
for changed code. A throwaway ad-hoc script in `%TEMP%` gets deleted and the evidence vanishes;
the durable fix is to commit a **canonical test file in the repo** (`test_license.py`) so
`python test_license.py` is the repeatable command. Same pattern applies to any deliverable.

## Pitfalls

- Keep the server repo **private** — a public license server exposes your pricing/business
  model. GitHub visibility switch via CDP: `#visibility_menu-button` → item with
  `data-show-dialog-id="visibility-menu-dialog-private"` → «I have read and understand» →
  «Make this repository private» (see `cdp-browser-automation` skill).
- `importlib` not imported in `main()` of the test file → NameError; add
  `import importlib.util` at top.
- uvicorn in a thread: set `uv.should_exit = True` and sleep ~0.5s before tempdir cleanup,
  else port lingers / file locked.
