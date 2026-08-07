# Dashboard breakage + boot chain — 2026-08-05 session detail

## The wrong-file trap (cost ~1h)

Two dashboard.html files exist on the host:
- `C:\ParanoidX-data\dashboard.html` — **the one the server serves** (`-data /mnt/c/ParanoidX-data`)
- `C:\Users\tomas\ParanoidX-data\dashboard.html` — a decoy that looks right

Sequence that misled: wrote patches to `C:\Users\tomas\ParanoidX-data\dashboard.html`, verified JS syntax on it, then discovered `curl localhost:8080/` still returned the OLD content. Root check:
```
curl -s http://127.0.0.1:8080/ | md5sum
md5sum /mnt/c/ParanoidX-data/dashboard.html
```
Only after copying to `/mnt/c/ParanoidX-data/dashboard.html` did md5 match. **Rule: md5 the served bytes vs the candidate file BEFORE editing, and again after.**

Note: `http://localhost:8080` works from Windows (WSL localhost forwarding); `http://127.0.0.1:8080` from Windows does NOT (only inside WSL). Browser caches the page — hard-refresh or `?v=`.

## Why the 51KB enhanced dashboard was broken (JS)

1. **Duplicate block-scoped declarations** — SyntaxError kills the whole `<script>`; page renders but every function is undefined (`loadProtocolsPage is not defined` in console). Seen:
   - `const services` twice in `loadVPNPage()`
   - `const tabs` then `let tabs` in `loadBridgeConfigPage()` (fixed by renaming to `tabsDef`)
2. **Duplicate function definitions** — a later `function refreshDashboard() { loadPage('dashboard'); }` shadowed the real async one → `Maximum call stack size exceeded` (refreshDashboard → loadPage → case 'dashboard' → refreshDashboard …).
3. **CSS conflict**: `.modal-overlay { display:none; ...; display:flex; }` — second `display` wins, modal always visible. Fix: base rule `display:none` only; `.active` gets `display:flex`.
4. **Outside-click handler** closed the modal immediately after opening (auth link isn't inside `.modal`). Exclude `a[onclick*="showAuthModal"], a[onclick*="switchAuthMode"]`.
5. **Field name mismatch**: modal login form sent `email`, server `/login` reads `username` → login POST returned 401/redirect but user never authenticated.

Detect all JS issues offline before deploying:
```
curl -s http://127.0.0.1:8080/ -o /tmp/d.html
python3 -c "import re; h=open('/tmp/d.html').read(); open('/tmp/d.js','w').write(re.search(r'<script>(.*?)</script>', h, re.S).group(1))"
node --check /tmp/d.js        # WSL: /mnt/c/Users/tomas/AppData/Local/hermes/node/node.exe
```
HTML tag balance: `len(re.findall('<div[\s>]', html)) == len(re.findall('</div>', html))` (182/182 when OK).

## Resolution: revert to simple version

User explicitly chose: "Вернуть простую РАБОЧУЮ версию (4951 байт) + аккуратно добавить логин". The 6.6KB final dashboard = original `internal/api/dashboard.html` CSS/HTML + corrected API field mapping (`disk.used_pct`, `system.ram_used_pct`, `system.load_1m`, `messages`) + `safeNum()` + `initAuth()` (fetch `/api/auth/me`, show username + Logout or Login link) + `esc()` for XSS. **Preference: simple+working over fancy+broken — verify visually in browser after deploy.**

## RAM / disk metrics truth

- RAM: NOT hardcoded. WSL2 default = ~50% of RAM visible to Windows (7.8 GB after BIOS UMA=16GB carve-out) → 3.8 GB. Fixed with `C:\Users\tomas\.wslconfig` (memory=5GB, processors=8, swap=4GB) + `wsl --shutdown`. Now 4917 MB.
- Disk: `diskUsage("/")` = WSL ext4 VHDX (1007 GB). Replaced all 6 call sites with `/mnt/c` → 464.5 GB real SSD.

## Boot chain (start before login)

1. systemd: `deploy/paranoidx.service` → `sudo systemctl daemon-reload && systemctl enable --now paranoidx`
2. Task Scheduler (SYSTEM, ONSTART, before login): XML task with `<BootTrigger><Delay>PT30S</Delay></BootTrigger>`, principal `<UserId>S-1-5-18</UserId>`, action `C:\Windows\System32\wsl.exe -d Ubuntu-24.04 -- /bin/true`. Creation requires admin → `.cmd` wrapper writing result to file, invoked via `powershell Start-Process cmd -ArgumentList '/c', '<wrapper>' -Verb RunAs -Wait` (UAC prompt; `-RedirectStandardOutput` is incompatible with `-Verb RunAs`). Verify: `schtasks /Query /TN ParanoidX-WSL2-Boot-System /V /FO LIST` (via admin cmd wrapper) → "Режим входа: Интерактивный/фоновый", "Запуск от имени: СИСТЕМА", "Тип расписания: При запуске компьютера".
3. Login-time fallbacks (no admin needed): HKCU Run value `ParanoidX-WSL2-Boot` → `wsl.exe -d Ubuntu-24.04 -- /bin/true`; Startup shortcut via WScript.Shell COM.
4. `wsl --shutdown` once → systemd auto-restarts paranoidx with new memory limits.

## Auth live-testing gotchas

- Server caches users in memory; editing `dashboard_users.json` while running is overwritten by `Authenticate()`'s save-on-login. Stop → edit → start.
- Min password 6 chars (changed from 8 in both `ChangePassword` and `CreateUser`).
- `POST /api/auth/register` self-registration → role `user`, `ForcePasswordChange=false`, 400 on duplicate.
- Login POST → 302; `/api/auth/me` (cookie `dashboard_token`) → `{"username","role","force_password_change"}`.
