---
type: textbook-entry
topic: "Claude + Obsidian Second Brain Architectures (10 Repos Analysis)"
status: "🔴 Не изучено"
created: "2026-08-09"
tags: ["#textbook", "#obsidian", "#claude", "#second-brain", "#mcp", "#skills", "#karpathy-wiki"]
---

# 10 Free GitHub Repos: Claude + Obsidian Second Brain

> **Source:** Tweet by @0xkkai (kai) — https://x.com/0xkkai/status/2085838657068347401 (Aug 8, 2026)
> **Full thread via fxtwitter:** https://fxtwitter.com/0xkkai/status/2085838657068347401

## The Three Architectures

Before the repos, understand the three patterns behind all of them:

### 1. Karpathy LLM Wiki Pattern (April 2026)
- **Structure:** `raw/` (source docs) → `wiki/` (compiled linked pages) → `instructions/` (rules)
- **Key move:** Claude reads each raw file **once**, extracts insights, writes to wiki, never touches raw again
- **Benefit:** 70-90% token savings on repeat queries; knowledge compounds instead of decaying
- **Repos:** #1, #4, #5, #10

### 2. Skills Architecture (Anthropic, July 2026)
- Folder system: drop `SKILL.md` in skills directory
- Claude reads description at startup; full skill loads only on trigger
- **Obsidian use:** "when I mention paper → activate paper-reader skill", "on vault open → load note-org convention"
- **Repos:** #3, #9

### 3. MCP Bridge (Model Context Protocol)
- Live bridge: Claude sends structured requests → server queries vault → returns results real-time
- **Read-only** (safe, pull data) vs **Read-write** (powerful, create/edit notes)
- Read-write enables "vault builds itself while you sleep"
- **Repos:** #2, #6, #7, #8

---

## The 10 Repos, Ranked

### 1. **AgriciDaniel/claude-obsidian** — Karpathy Wiki Pattern (purest)
- **What:** Drop any source (PDF, MD, web clip, transcript) into `raw/` → Claude compiles to 8-15 linked wiki pages
- **Setup:** Medium (Claude Code plugin, 20-30 min initial config)
- **Best for:** First Karpathy pattern implementation, canonical reference
- **Limitations:** Opinionated folder structure, no semantic search, not for teams
- **Verdict:** Start here for first knowledge vault. Skip if 500+ notes in different structure.

### 2. **eugeniughelbur/obsidian-second-brain** — MCP (read-write) + Skills + Custom Commands
- **What:** Persistent memory for Claude Code + 6 other CLI agents. 45 named commands:
  - Hybrid semantic search (BM25 + embeddings)
  - Self-rewriting notes (update on contradiction)
  - Key-less web research (public search)
  - **Scheduled agents** (lint wiki nightly, dedupe weekly, resurface stale monthly)
- **Setup:** High initially (local embeddings ~4GB RAM, scheduler config), then hands-off
- **Best for:** Power users with 1,000+ notes who want zero maintenance
- **Killer feature:** Scheduled agents run autonomously
- **Limitations:** 90 min docs reading, Claude Code specific commands
- **Verdict:** Most powerful. Reach for it when vault outgrows manual maintenance.

### 3. **kepano/obsidian-skills** — Skills (Anthropic-native)
- **What:** Pre-built skills by Kepano (Obsidian creator). Works with Claude Code, Codex, Open Code.
- **Setup:** Low (clone to skills folder, auto-registers)
- **Best for:** Obsidian-fluent users wanting "official-ish" defaults
- **Limitations:** Skills-only, no MCP (no live queries), fewer skills than ecosystem clones
- **Verdict:** Safest bet for deep Obsidian mindset. High trust factor.

### 4. **qhuang20/obsidian-skills** — Skills + Karpathy Wiki Pattern
- **What:** Claude Code plugin with dedicated `llm-wiki` skill + utility skills
- **Setup:** Low-medium (standard plugin install + one config file for naming conventions)
- **Best for:** Want Karpathy pattern without building from scratch; faster than #1 if in Claude Code
- **Limitations:** Less battle-tested, utility skills overlap with #3/#5
- **Verdict:** Solid if living in Claude Code. Consider #1 for reference, #5 for pure Karpathy.

### 5. **ekadetov/llm-wiki** — Karpathy Wiki Pattern (pure play)
- **What:** Only the Karpathy pattern as Claude Code plugin. 6 commands: ingest, query, save, lint
- **Setup:** Very low (install → point at vault → `/init` → working in 5 min)
- **Best for:** Purists wanting exact Karpathy implementation, nothing else
- **Limitations:** No semantic search, no scheduled agents, no MCP (deliberately minimal)
- **Verdict:** Best minimum-viable Karpathy. Great start, may outgrow.

### 6. **iansinnott/obsidian-claude-code-mcp** — MCP (read-write via Obsidian Plugin)
- **What:** Obsidian plugin running MCP server inside Obsidian. Claude queries → reads/creates/modifies notes, follows backlinks, updates graph via Obsidian API
- **Setup:** Medium (community plugin + MCP endpoint in Claude Code config, Obsidian must run)
- **Best for:** Live Obsidian interaction respecting plugins, templates, dataview
- **Unique:** Only repo going through Obsidian's own API (file safety)
- **Verdict:** For live vault interaction with full Obsidian ecosystem.

### 7. **Repo #7** — (details in thread, MCP family)
- Architecture: MCP Bridge
- [Need to fetch full details from thread]

### 8. **Repo #8** — (details in thread, MCP family)
- Architecture: MCP Bridge
- [Need to fetch full details from thread]

### 9. **Repo #9** — (details in thread, Skills family)
- Architecture: Skills
- [Need to fetch full details from thread]

### 10. **Repo #10** — (details in thread, Karpathy Wiki family)
- Architecture: Karpathy Wiki Pattern
- [Need to fetch full details from thread]

---

## Decision Matrix: Which to Choose?

| Your Situation | Start With |
|---|---|
| New to all this, empty vault | **#1 AgriciDaniel/claude-obsidian** (cleanest Karpathy) |
| Want minimum viable, 5 min setup | **#5 ekadetov/llm-wiki** (pure Karpathy) |
| Already in Obsidian ecosystem | **#3 kepano/obsidian-skills** (native conventions) |
| Live in Claude Code, want Karpathy + skills | **#4 qhuang20/obsidian-skills** |
| 1,000+ notes, want automation | **#2 eugeniughelbur/obsidian-second-brain** (scheduled agents) |
| Need live Obsidian API (dataview, plugins) | **#6 iansinnott/obsidian-claude-code-mcp** |
| Team use, self-hosted | Consider #2 or #6 with shared vault |

---

## Practical Application for Our Stack

### Current State
- We have: **Obsidian Vault** (`C:\Vault`), **Hermes Agent** with skills, **Graph Engineering** workflow
- We use: `textbook_learn.py` cron (every 6h), `export_graph_to_vault.py`, `chronicle.md`
- Missing: Automated ingestion, semantic search, scheduled maintenance, live AI-vault bridge

### Recommended Integration Path

#### Phase 1: Karpathy Wiki Pattern (Immediate)
- Adopt `raw/` → `wiki/` → `instructions/` structure in Vault
- Modify `textbook_learn.py` to write learned topics to `wiki/` as linked pages
- Use `chronicle.md` as the "instructions" layer (rules that prevent drift)

#### Phase 2: Skills Architecture (Hermes Native)
- Our skills already follow this: `SKILL.md` with trigger descriptions
- Hermes auto-loads skills on trigger → matches Anthropic pattern exactly
- **Action:** Document our skill conventions as a "skill pack" for Obsidian

#### Phase 3: MCP Bridge (High Value)
- Deploy **iansinnott/obsidian-claude-code-mcp** (Obsidian plugin + MCP server)
- Hermes Agent → MCP → live vault queries (read/write)
- Enables: "query vault for all YOLO configs", "create note from radio transcript"

#### Phase 4: Scheduled Agents (eugeniughelbur pattern)
- Add cron jobs that run Hermes with specific skills:
  - Nightly: lint wiki, fix broken links
  - Weekly: deduplicate similar notes (embedding-based)
  - Monthly: resurface stale 🟢 topics for review

---

## Repo Links to Clone

```bash
# Phase 1: Karpathy Wiki
git clone https://github.com/AgriciDaniel/claude-obsidian
git clone https://github.com/ekadetov/llm-wiki

# Phase 2: Skills
git clone https://github.com/kepano/obsidian-skills
git clone https://github.com/qhuang20/obsidian-skills

# Phase 3: MCP Bridge
git clone https://github.com/iansinnott/obsidian-claude-code-mcp

# Phase 4: Full Second Brain (when ready)
git clone https://github.com/eugeniughelbur/obsidian-second-brain
```

---

## Next Steps

- [ ] Clone #1 and #5, evaluate folder structure for our Vault
- [ ] Create `raw/`, `wiki/`, `instructions/` in `C:\Vault`
- [ ] Patch `textbook_learn.py` to output to `wiki/` with wikilinks
- [ ] Install Obsidian community plugin for MCP (iansinnott)
- [ ] Configure Hermes MCP client to talk to Obsidian MCP server
- [ ] Add scheduled cron jobs for vault maintenance (lint, dedupe, resurface)
- [ ] Document chosen architecture in skill: `obsidian-second-brain-architecture`

---

## Key Insight for Our Graph Engineering

The **Karpathy Wiki Pattern** is essentially what our **Graph Evolution Protocol** does:
- `raw/` = source documents (PRD, research, logs)
- `wiki/` = compiled nodes in graph.yaml (linked, deduplicated)
- `instructions/` = EVOLUTION/PROJECT_PLAN.md (rules preventing drift)

Our `textbook_learn.py` cron = automated ingestion agent.
Our `chronicle.md` = audit trail of what was learned.
Our `graph.yaml` = the living wiki that compounds.

**We're already implementing this pattern.** The tweet repos just give us battle-tested tooling to accelerate it.