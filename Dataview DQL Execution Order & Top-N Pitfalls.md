Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, obsidian, dataview, dql, query-pipeline, performance]
source: textbook
status: learned
date: 2026-08-10
priority: 9
---

# Dataview DQL Execution Order & Top-N Pitfalls

## Summary
Dataview Query Language (DQL) is a **pipeline**, not SQL. Commands execute **top-to-bottom, line-by-line**. The order of `WHERE`, `SORT`, `LIMIT`, `GROUP BY` fundamentally changes results. Misordering is the #1 cause of "wrong Top-N" bugs.

## Pipeline Execution Model

```
SOURCE (FROM) 
    → FILTER (WHERE) 
    → TRANSFORM (FLATTEN) 
    → SORT 
    → GROUP BY 
    → LIMIT 
    → OUTPUT (TABLE/LIST/TASK)
```

Each line **passes its result set to the next line**. No optimization/reordering occurs.

## Critical Pitfalls

### 1. LIMIT Before SORT = Wrong Top-N
```dataview
# ❌ WRONG: Limits FIRST, then sorts those 5
LIMIT 5
SORT file.mtime DESC
# Result: 5 random files, then sorted among themselves

# ✅ CORRECT: Sorts ALL, then takes top 5
SORT file.mtime DESC
LIMIT 5
```

### 2. WHERE After SORT = Wasted Work
```dataview
# ❌ INEFFICIENT: Sorts all files, then filters
SORT file.mtime DESC
WHERE file.tags contains "#project"

# ✅ EFFICIENT: Filters FIRST, then sorts fewer
WHERE file.tags contains "#project"
SORT file.mtime DESC
```

### 3. GROUP BY Resets Sort Order
```dataview
# ❌ Sort lost after GROUP BY
SORT file.mtime DESC
GROUP BY file.folder
LIMIT 3

# ✅ Sort WITHIN groups
GROUP BY file.folder
SORT rows.file.mtime DESC
LIMIT 3  # Limits GROUPS, not rows!
```

### 4. FLATTEN Explodes Row Count Before LIMIT
```dataview
# ❌ FLATTEN creates 1000 rows, LIMIT 10 takes first 10
FLATTEN file.tasks as task
WHERE !task.completed
LIMIT 10

# ✅ Filter FIRST, then flatten
WHERE !task.completed
FLATTEN file.tasks as task
LIMIT 10
```

### 5. LIMIT on GROUP BY Limits Groups, Not Rows
```dataview
GROUP BY file.folder
LIMIT 5
# Returns 5 FOLDERS, each with ALL its files
# To limit rows per group: use `LIMIT 5` INSIDE `rows` in DataviewJS
```

## Performance Rules

| Operation | Complexity | Best Position |
|-----------|------------|---------------|
| `FROM` / `WHERE` | O(n) scan | **First** — reduces working set |
| `FLATTEN` | O(n×m) expansion | After WHERE, before SORT |
| `SORT` | O(n log n) | After filtering/flattening |
| `GROUP BY` | O(n) hash | After SORT if you need sorted groups |
| `LIMIT` | O(1) truncate | **Last** (or after GROUP BY for group limit) |

## Optimization Checklist

- [ ] `FROM` specifies narrowest folder/tag possible
- [ ] All `WHERE` clauses before `SORT`/`GROUP BY`
- [ ] `FLATTEN` after filtering, not before
- [ ] `SORT` before `LIMIT` (always)
- [ ] `LIMIT` as late as possible
- [ ] Avoid `SORT` on computed fields in large vaults — use indexed metadata (`file.mtime`, `file.ctime`, `file.size`)

## DataviewJS for Complex Top-N Per Group

```dataviewjs
// Top 3 tasks per project (impossible in pure DQL)
const pages = dv.pages("#project")
  .where(p => p.tasks)
  .flatMap(p => p.tasks
    .where(t => !t.completed)
    .map(t => ({project: p.file.link, task: t, date: t.due}))
  )
  .sort(t => t.date)
  .groupBy(t => t.project)
  .map(g => g.rows.slice(0, 3))
  .flat()

dv.table(["Project", "Task", "Due"], 
  dv.array(dv.pages("#project")).flatMap(p => 
    p.tasks.where(t => !t.completed).slice(0,3).map(t => [p.file.link, t.text, t.due])
  ))
```

## Application to Our Vault

### Evolution Dashboard Queries (Optimized)
```dataview
# ✅ Correct: Filter → Sort → Limit
TABLE type, status, file.mtime as "Updated"
FROM #evolution
WHERE status = "alive"
SORT file.mtime DESC
LIMIT 20

# ✅ Grouped with internal sort
TABLE type, rows.file.link as "Nodes"
FROM #evolution
WHERE status = "alive"
GROUP BY type
SORT rows.file.mtime DESC
```

### Inbox Processing (Top-N per tag)
```dataviewjs
// Top 5 newest per tag in Inbox
const byTag = dv.pages("Inbox")
  .flatMap(p => p.file.etags.map(t => ({tag: t, page: p, date: p.file.ctime})))
  .groupBy(t => t.tag)
  .map(g => g.rows.sort(t => t.date, 'desc').slice(0, 5))

dv.table(["Tag", "File", "Created"], 
  byTag.flatMap(g => g.rows.map(r => [g.key, r.page.file.link, r.date]))
)
```

## Anti-Patterns in Our Codebase

| Query | Problem | Fix |
|-------|---------|-----|
| `LIMIT 10` then `SORT` | Wrong top 10 | Swap order |
| `SORT` on `file.name` for 5000 files | Slow | Sort on `file.mtime` or indexed field |
| `FLATTEN tasks` before `WHERE !completed` | Explodes rows | Filter first |
| `GROUP BY` without internal sort | Random order in groups | `SORT rows.field` |

## References
- Official: https://blacksmithgu.github.io/obsidian-dataview/queries/structure/
- Complete Guide: https://www.dsebastien.net/the-complete-guide-to-dataview-in-obsidian/
- Pipeline Mental Model: "DQL is a pipeline, not SQL" — official docs
C:\Vault\Dataview DQL Execution Order & Top-N Pitfalls.md


