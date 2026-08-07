---
name: paranoidx-onboarding-evolution
description: Fix ParanoidX onboarding + node monitor with Telegram boot.
category: mlops
---

# ParanoidX Onboarding & Node Monitor Evolution

## Goal
Make ParanoidX have a **fully working, beautiful, logical onboarding flow** and **auto-starting node monitor** that:
1. Boots on Windows restart
2. Brings up WSL, VPN bridge, all services
3. Reports progress to Telegram at each step
4. Dashboard accessible via onion + clearnet

## Trigger
Use when: "ParanoidX onboarding broken" or "need node monitor autostart"

## Phase 1: Fix Onboarding UX (Cycles 1-5)
- [ ] Fix login.html → cookie + redirect flow (SameSite: Lax, Secure, path=/)
- [ ] Register with invite: real mnemonic generation, display once, force save
- [ ] Restore from seed: validate BIP39, match pubkey, reset password, auto-login
- [ ] Dashboard: show onboarding status (wallet linked, citizen, silver balance)
- [ ] First-visit wizard: invite → register → mnemonic backup → citizen claim → done

## Phase 2: Node Monitor Service (Cycles 6-10)
- [ ] Create `node_monitor.py` (runs in WSL, systemd service)
- [ ] Steps: WSL up → Docker up → Tor up → V2Ray up → ParanoidX binary up → Health checks
- [ ] Each step → Telegram message: "🔄 Starting Tor..." → "✅ Tor ready (onion: abc123.onion)"
- [ ] Retry logic with backoff, max 3 retries per service
- [ ] systemd unit: `paranoidx-node-monitor.service` (Type=notify, Restart=always)

## Phase 3: Windows Autostart (Cycles 11-15)
- [ ] Windows Task Scheduler: "ParanoidX Node Monitor" → triggers at boot, runs `wsl -d Ubuntu-24.04 -- systemctl start paranoidx-node-monitor`
- [ ] Or WSL systemd: enable `paranoidx-node-monitor.service` + `systemctl enable` in WSL
- [ ] Ensure Docker Desktop starts first (already in Run registry)

## Phase 4: Dashboard Polish (Cycles 16-20)
- [ ] Real-time status websocket: service health, bridge, onion address
- [ ] One-click "Restart Node" button (calls monitor API)
- [ ] Version badge auto-increment visible in header
- [ ] Dark/light theme toggle, persisted
- [ ] Mobile-responsive sidebar collapse

## Key APIs to Implement
- `POST /api/node/start` — trigger monitor start sequence
- `GET /api/node/status` — current step, services, onion address
- `WS /api/node/ws` — real-time updates
- `GET /api/onboarding/status` — wallet, citizen, invite, silver

## Telegram Bot
- Token from `simplex-node.json` (`torquemada_token`, `torquemada_chat_id`)
- Format: HTML, emoji per step
- Error alerts: 🔴 Critical, 🟡 Warning, 🟢 OK

## Files to Create/Modify
- `/c/ParanoidX/scripts/node_monitor.py` — main monitor
- `/c/ParanoidX/scripts/telegram.py` — notifier
- `/etc/systemd/system/paranoidx-node-monitor.service` — systemd unit
- `/c/ParanoidX/internal/api/node_monitor.go` — API handlers
- `/c/ParanoidX-data/login.html`, `register.html`, `dashboard.html` — UX fixes
- `/c/ParanoidX/scripts/evolution_cycle.py` — update to run monitor tests

## Acceptance Criteria
1. Fresh Windows boot → 2 min → Dashboard at `https://<onion>.onion` + `https://localhost:8080`
2. Telegram gets 6-8 messages during boot
3. New user: invite → register → sees mnemonic → saves → citizen → dashboard
4. Existing user: seed restore → password reset → dashboard
5. All 16 dashboard tabs show real API data (no placeholders)