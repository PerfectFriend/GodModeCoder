---
name: desktop-app-rendering-debugging
description: "Debug Electron/React desktop render crashes, stack overflow."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, electron, react, desktop, rendering, stack-overflow, troubleshooting]
    related_skills: [systematic-debugging, hermes-agent]
---

# Desktop App Rendering Debugging

## Overview

Electron/React desktop apps (like Hermes Desktop, VS Code, Discord, Slack) can hit **renderer-process stack overflows** when trying to render large conversation histories, massive message payloads, or deeply nested component trees. This skill covers the systematic approach to diagnose and recover from these crashes.

## When to Use

Use when a desktop app:
- Shows blank/black screen on launch
- Crashes with `RangeError: Maximum call stack size exceeded` in renderer console
- Freezes when opening a specific session/tab/project
- Has UI that works in CLI/TUI but not in desktop
- Shows `[error-boundary]` crashes in logs for specific components

## Root Cause Pattern

| Symptom | Typical Cause |
|---------|---------------|
| Stack overflow on session list render | Session with 100+ messages + large tool outputs |
| Blank screen on startup | Last-open session triggers recursive render |
| Freeze on specific tab | Component tree depth exceeds JS stack limit (~10-15k frames) |
| Error boundary loops | Component throws during render, boundary re-renders, throws again |

## Diagnostic Steps (Phase 1: Root Cause)

### 1. Check Renderer Logs

**Hermes Desktop:** `~/.hermes/logs/desktop.log`
```bash
grep -i "Maximum call stack\|RangeError\|error-boundary" ~/.hermes/logs/desktop.log
```

**VS Code:** `~/Library/Logs/Code/renderer*.log` (macOS) / `%APPDATA%\Code\logs\renderer*.log` (Windows)

**Generic Electron:** Enable `--enable-logging --log-level=0` and check console

### 2. Identify the Triggering Entity

Look for patterns in logs:
- `session-tile:SESSION_ID` → specific session causes crash
- `message-list` / `conversation-view` → message rendering issue
- `sidebar` / `session-list` → list rendering issue

### 3. Verify Data vs UI

**Critical distinction:** The data is usually fine (in SQLite/state.db). Only the **renderer** fails.

```bash
# Hermes: verify session exists in DB
sqlite3 ~/.hermes/state.db "SELECT id, title, message_count FROM sessions WHERE id='PROBLEMATIC_ID';"

# If message_count > 100 and last message has large content → confirmed
```

## Recovery Procedure (Phase 4: Implementation)

### Step 1: Export Data (Preserve Everything)

```bash
# Hermes
hermes sessions export PROBLEMATIC_SESSION_ID --output ~/session-backup.jsonl

# VS Code: File → Export → Workspace/Profile
# Generic: Copy relevant DB/files before deletion
```

### Step 2: Remove Trigger from UI Index

```bash
# Hermes: delete from routing index + state.db
hermes sessions delete PROBLEMATIC_SESSION_ID

# VS Code: Delete workspace storage
rm -rf ~/.config/Code/User/workspaceStorage/PROBLEMATIC_HASH/

# Generic Electron: Clear localStorage/IndexedDB for the origin
```

### Step 3: Restart Clean

```bash
# Kill all renderer + main processes
pkill -f "Hermes.*desktop"  # or app-specific
# Restart
hermes desktop
```

### Step 4: Verify & Restore Context

- App launches cleanly
- Create new session
- Import key context from exported JSONL if needed

## Prevention Patterns

| Pattern | Implementation |
|---------|----------------|
| Auto-compress long sessions | `session.auto_compress_threshold: 80` in config |
| Limit message payload size | Truncate tool outputs > 50KB before storing |
| Virtualize lists | React-window / react-virtual for session/message lists |
| Error boundary isolation | Wrap each session-tile in independent boundary |
| Lazy-load heavy content | Load message bodies on expand, not on list render |

## Hermes-Specific Reference

### Log Locations
```
~/.hermes/logs/desktop.log       # Renderer console (stack traces here)
~/.hermes/logs/agent.log         # Main process
~/.hermes/logs/errors.log        # Aggregated errors
~/.hermes/state.db               # Canonical session store (SQLite)
~/.hermes/sessions/sessions.json # Gateway routing mirror
```

### Key Commands
```bash
hermes sessions list              # See all sessions with message counts
hermes sessions export ID -o file # Backup before delete
hermes sessions delete ID         # Remove from UI index
hermes doctor --fix               # Check config health
hermes gateway restart            # If gateway also stuck
```

### Config for Prevention
```yaml
# ~/.hermes/config.yaml
session:
  auto_compress_threshold: 80    # Compress at 80 messages
  compression_keep_recent: 15    # Keep 15 recent turns
display:
  max_message_preview_chars: 5000  # Truncate previews in lists
```

## Debugging Workflow Summary

```
1. READ renderer logs → find SESSION_ID in error-boundary tag
2. QUERY state.db → confirm message_count > 100 + large last message
3. EXPORT session → JSONL backup (data preserved)
4. DELETE session → removes from UI render target
5. RESTART desktop → clean launch
6. RESTORE context → new session + key excerpts from backup
```

## Related Skills

- `systematic-debugging` — General 4-phase methodology (Phase 1-4 map directly)
- `hermes-agent` — CLI reference, config, session management commands

## Reference Files

- `references/hermes-desktop-stack-overflow.md` — Reproduction recipe, recovery commands, and prevention config from live session