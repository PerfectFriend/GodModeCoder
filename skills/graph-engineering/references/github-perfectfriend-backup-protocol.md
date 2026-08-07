# GitHub PerfectFriend Backup Protocol

Документирует рабочий процесс бекапа эволюционного графа в приватный репозиторий PerfectFriend.

## Репозиторий
- **Owner:** PerfectFriend (Chrome logged in)
- **Repo:** `GodModeCoder-backup` (Private)
- **URL:** https://github.com/PerfectFriend/GodModeCoder-backup
- **Branches:** `master` (source), `main` (synced)

## Sync Workflow (Local + Browser CDP)

### 1. Local Merge + Push
```bash
cd C:\Vault
git checkout main 2>/dev/null || git checkout -b main
git merge master --allow-unrelated-histories -m "merge: master into main"
git push origin main
git push origin master
```

### 2. Browser Verify (Chrome CDP)
- Repo page: **Private** ✓
- Branches: `main` & `master` synced ✓

## Make Private (Chrome CDP) — Working Pattern

**Critical**: GitHub settings forms use Turbo. Form `submit()` fails silently due to Turbo interception. Use button-click flow.

```python
# 1. Navigate to settings
browser_navigate("https://github.com/PerfectFriend/<REPO>/settings")

# 2. Wait for Turbo ready (8-10s)
time.sleep(10)

# 3. Click "Change visibility" button (visible in Danger Zone)
btn = find_button("Change visibility")
btn.click()
time.sleep(2)

# 4. Click "Change to private" in modal
btn = find_button("Change to private")
btn.click()
time.sleep(2)

# 5. Click "I want to make this repository private"
btn = find_button("I want to make this repository private")
btn.click()
time.sleep(3)

# 6. Verify: repo page shows "Private"
```

**Anti-patterns that FAIL:**
- ❌ `form.submit()` — Turbo intercepts
- ❌ `form.requestSubmit()` — Turbo intercepts  
- ❌ `FormData` + `form.submit()` — Turbo intercepts
- ❌ GitHub REST API with cookies — 401 (requires PAT)

## Merge Branches (Local Git) — Recommended
Avoid GitHub UI PR flow and Turbo issues entirely:

```bash
cd C:\Vault
git checkout main 2>/dev/null || git checkout -b main
git merge master --allow-unrelated-histories -m "merge: master into main"
git push origin main
git push origin master
```

## Repo Structure (GodModeCoder-backup)

```
.obsidian/
  graph.json          # 9 colorGroups, filtered, arrows
  graph-colors.css    # Типы/статусы/рёбра цвета
  workspace.json      # Layout
Evolution/
  *.md (13 узлов)     # Все с тегами #type/*, #status/*, #evolution/graph
  INDEX.md            # Таблица + рёбра + fitness
  Graph Dashboard.md  # Dataview: живая таблица, статистика, рёбра
  Dead Nodes Dashboard.md # План реанимации мёртвых
  Presets/            # Full Graph, Alive Only, Commercial, Radio
  chronicle.md        # История мутаций + обучение
Учебник.md            # 32 темы для изучения (крон каждые 6ч)
hermes-verify-all.py  # 10 тестов (все проходят)
export_graph_to_vault.py # Cron wrapper (каждые 6ч)
textbook_learn.py     # Auto-learning cron (каждые 6ч)
AUDIT_GRAPH_ENGINEERING_OBSIDIAN.md # Полный аудит
```

## Cron Jobs (Hermes)

| Job | Schedule | Script | Skills |
|-----|----------|--------|--------|
| `graph-pulse-export` | every 6h | `export_graph_to_vault.py` | `obsidian-graph-engineering` |
| `textbook-learning` | every 6h | `textbook_learn.py` | `obsidian-graph-engineering` |

## Key Files in Grimoire

| Path | Purpose |
|------|---------|
| `ru/configs/graph.yaml` | Source of Truth графа |
| `ru/scripts/export_graph_to_obsidian.py` | Экспортёр в Vault |
| `ru/scripts/pulse.py` | Пульс/health-check |
| `ru/scripts/hermes-verify-all.py` | Auto-test suite (10 тестов) |
| `ru/scripts/export_graph_to_vault.py` | Cron wrapper |
| `ru/scripts/textbook_learn.py` | Auto-learning cron |