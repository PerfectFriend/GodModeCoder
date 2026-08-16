---
type: textbook-entry
topic: "Penpot — Open-Source Design Platform"
status: "🔴 Не изучено"
created: "2026-08-09"
tags: ["#textbook", "#design-code", "#open-source", "#self-hosted", "#design-systems"]
---

# Penpot — Open-Source Design Platform

> **Source:** https://penpot.app | https://penpot.app/features
> **Tweet reference:** https://x.com/i/status/2086107198640300369 (reply by Valen, Aug 8 2026)

## What is Penpot?

Penpot is the **first open-source design platform** for teams building digital products at scale. Built on open standards (SVG), available as web-based or **self-hosted**.

**Company:** Kaleidos (founded 2021)
**License:** MPL-2.0 (Mozilla Public License)
**Repo:** https://github.com/penpot/penpot

## Key Features

- ✅ **Open-source** — full code transparency, self-hostable
- ✅ **Web-based** — runs in browser, no install needed (SaaS or self-hosted)
- ✅ **SVG-native** — designs are standard SVG, interoperable
- ✅ **Design Systems** — components, libraries, tokens, sync with code
- ✅ **Collaborative** — real-time multiplayer, comments, handoff
- ✅ **Code-friendly** — inspect CSS, SVG, React, HTML; design tokens export
- ✅ **AI-ready** — open API, community building AI integrations

## Core Capabilities

### Design Tools
- Vector editing (pen, shapes, boolean ops)
- Flex Layout (CSS Flexbox-based auto-layout)
- Components & instances (like Figma)
- Libraries (shared across files/teams)
- Design tokens (colors, typography, spacing, border, effects)

### Design Systems
- **Libraries** — publish/share components across projects
- **Tokens** — JSON/SCSS/CSS export for developers
- **Component playground** — interactive docs for devs
- **Version history** — branch/merge design changes

### Developer Handoff
- Inspect panel: CSS, SVG, React, HTML, Tailwind
- Copy code snippets directly
- Design token export (JSON, SCSS, CSS custom properties)
- Asset export (SVG, PNG, WebP, PDF)

### Self-Hosting
```bash
# Docker Compose (recommended)
docker compose up -d
# Services: penpot-frontend, penpot-backend, penpot-exporter, postgres, redis
```

**Requirements:** Docker, 4GB+ RAM, 2+ CPU cores

## Why Penpot for Sovereign/ParanoidX Stack

| Requirement | Penpot Fit |
|---|---|
| **Self-hosted** | ✅ Full control, no cloud dependency |
| **Open standards** | ✅ SVG, CSS, JSON — no vendor lock-in |
| **Design systems as code** | ✅ Tokens export to codebase directly |
| **AI integration ready** | ✅ Open API, community MCP servers |
| **Sovereign infrastructure** | ✅ Runs on own K8s/Docker, air-gapped possible |
| **Team collaboration** | ✅ Real-time, comments, permissions |

## Comparison: pen.dev vs Penpot

| Aspect | pen.dev | Penpot |
|---|---|---|
| **Paradigm** | Design in IDE (local) | Design in browser (web/self-hosted) |
| **File format** | `.pen` (proprietary text) | SVG + JSON (open standards) |
| **AI integration** | Native (Codex, Cursor, Claude) | Via API/community |
| **Self-hosted** | No (extension only) | ✅ Full stack |
| **Cost** | Free (currently) | Free (open source) |
| **Team collab** | Git-based | Real-time multiplayer |
| **Design tokens** | Variables in `.pen` | Full token system + export |

## Integration Points for Our Stack

1. **Graph Engineering**: Penpot components as graph nodes
2. **Obsidian**: Design decisions documented alongside components
3. **Hermes Agent**: Skills can query Penpot API for design tokens
4. **ParanoidX**: Self-hosted design platform on sovereign infra
5. **Radio/SuperGuard**: Dashboard UI design in Penpot → code export

## Next Steps

- [ ] Deploy Penpot self-hosted (Docker Compose on local/server)
- [ ] Create design system library for SuperGuard dashboard
- [ ] Export design tokens → integrate into SuperGuard frontend
- [ ] Test AI workflow: ask agent to generate UI from Penpot tokens
- [ ] Compare workflow with pen.dev for different use cases
- [ ] Document in skill: `penpot-self-hosted-deployment`

## References

- https://penpot.app
- https://penpot.app/features
- https://github.com/penpot/penpot
- https://penpot.app/about
- Community: Discord, GitHub Discussions
- Tweet thread: midudev + Valen reply (Aug 8 2026)