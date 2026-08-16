---
type: textbook-entry
topic: "pen.dev — Design in IDE, Land in Code"
status: "🔴 Не изучено"
created: "2026-08-09"
tags: ["#textbook", "#design-code", "#AI-design", "#IDE"]
---

# pen.dev — Design in IDE, Land in Code

> **Source:** https://pen.dev | https://www.pen.dev/docs
> **Tweet reference:** https://x.com/i/status/2086107198640300369 (midudev, Aug 8 2026)

## What is pen.dev?

pen.dev is a **vector design tool that runs directly inside your IDE** (VS Code, Cursor, etc.). Unlike traditional design tools (Figma, Sketch) that run in separate browser tabs/apps, pen.dev lives alongside your code.

**Tagline:** "Design on canvas. Land in code."

## Key Features (from midudev tweet + docs)

- ✅ **Generates interfaces and lets you edit them live** — visual canvas inside IDE
- ✅ **Works with Codex, Cursor, Claude Code** — AI-assisted design workflows
- ✅ **Cross-platform:** Windows, macOS, Linux
- ✅ **Currently FREE** (as of Aug 2026)
- ✅ **`.pen` file format** — design as code, version-controllable
- ✅ **Design Libraries** — reusable components, variables, slots
- ✅ **Import/Export** — Figma, SVG, React, HTML/CSS

## Core Concepts (from docs)

### `.pen` Files
- Design files stored as structured text (like code)
- Version control friendly — diffable, mergeable
- Contain: components, variables, slots, design tokens

### Design ↔ Code Sync
- Components in `.pen` map 1:1 to code components
- Variables = design tokens (colors, spacing, typography)
- Slots = component composition points
- AI can read `.pen` files and generate matching code

### AI Integration
- Works with Codex, Cursor, Claude Code
- AI can: create components, modify designs, sync with codebase
- Design libraries (`lib.pen`) provide primitives for AI to use

## Installation

```bash
# VS Code / Cursor extension
# Search "pen.dev" in extensions marketplace
# Or: code --install-extension pen-dev.pen
```

## Workflow

1. Open `.pen` file in IDE → visual canvas appears
2. Design components using vector tools
3. Define variables (colors, spacing) and slots
4. Save → `.pen` file updates
5. AI assistant reads `.pen` → generates/updates React/Vue/Svelte components
6. Design system stays in sync with codebase

## Why This Matters for Our Stack

| Current Pain Point | pen.dev Solution |
|---|---|
| Figma → code handoff breaks | Design lives in repo, AI generates code |
| Design tokens drift | Variables in `.pen` = single source of truth |
| AI generates wrong UI | AI reads actual design primitives from `lib.pen` |
| Context switching (browser ↔ IDE) | Everything in one window |

## Integration Points

- **Graph Engineering**: `.pen` files as graph nodes (design → code edges)
- **Obsidian**: Document design decisions alongside `.pen` files
- **Hermes Agent**: Skills can read `.pen` files to generate UI code
- **ParanoidX**: Sovereign design tool (self-hosted, no cloud dependency)

## Next Steps

- [ ] Install pen.dev extension in Cursor/VS Code
- [ ] Create first `.pen` file with design system primitives
- [ ] Test AI workflow: ask Claude Code to generate component from `.pen`
- [ ] Compare with Penpot for open-source alternative
- [ ] Document workflow in skill: `design-code-integration`

## References

- https://pen.dev
- https://www.pen.dev/docs
- https://github.com/pen-dev/pen.dev (if exists)
- Tweet: midudev Aug 8 2026 — "Si Figma y Claude Code tuvieran un hijo, sería esto"