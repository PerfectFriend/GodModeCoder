# Evolution Cycle & Backup System

## Autonomous Evolution (20 cycles)
Script: `C:\ParanoidX\scripts\evolution_cycle.py`
Cron job: `paranoidx-evolution-cycle` (every 2h)

### Each Cycle (1 of 20):
1. **Pre-cycle backup** → `D:\backups\paranoidx-evolution-A{ver}-cycle{num}-{timestamp}.tar.gz`
   - Backs up: `C:\ParanoidX` + `C:\ParanoidX-data`
   - **MANDATORY: USB drive D:\ only — forbidden C:\ or WSL paths**
2. **Build Go binary** → `go build -o /home/tomas/bin/ParanoidX ./cmd/ParanoidX`
3. **Restart server** → `pkill -f ParanoidX && nohup /home/tomas/bin/ParanoidX ...`
4. **Run tests** → Verify all 16 dashboard API endpoints return real data
5. **Increment version badge** → A07→A08→A09... in dashboard.html, login.html, register.html
6. **Post-cycle backup** → Same D:\backups location
7. **Telegram report** → Cycle status, version, test results

## Cron Configuration
```json
{
  "job_id": "cca91e6c1ae2",
  "name": "paranoidx-evolution-cycle",
  "schedule": "every 120m",
  "script": "evolution_cycle.py 1",
  "workdir": "C:\\ParanoidX",
  "deliver": "telegram",
  "skills": ["paranoidx-evolution-deployment"]
}
```

## Backup Requirements
- **Target**: `D:\backups` (USB drive) — **ONLY acceptable location**
- **Format**: tar.gz with timestamped folder structure
- **Contents**: Full ParanoidX source + data dir (users.json, invites.json, certs, configs)
- **Frequency**: Pre-cycle + post-cycle (2 backups per cycle)

## Version Badge Increment
- Location: `dashboard.html`, `login.html`, `register.html`
- Format: `<span class="version-badge" id="dashVersion">A07</span>`
- Increment: A06 → A07 → A08 (sequential per cycle)
- Pattern: `id="dashVersion"[^>]*>([A-Z]\d+)<`