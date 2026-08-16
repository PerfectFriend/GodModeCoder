---
type: textbook-entry
topic: "AI-Assisted Design-to-Code Workflows"
status: "🔴 Не изучено"
created: "2026-08-09"
tags: ["#textbook", "#AI-design", "#design-to-code", "#workflows", "#Claude-Code"]
---

# AI-Assisted Design-to-Code Workflows

> **Source:** pen.dev docs, midudev tweet, Penpot AI integrations, community patterns

## The Core Problem

Traditional design-to-code handoff is broken:
1. Designer creates in Figma/Sketch
2. Developer manually translates to code
3. Design tokens drift, components diverge
4. AI generates UI but hallucinates designs (no design system context)

## New Paradigm: Design → AI → Code (Single Loop)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Design Tool │────▶│    AI Agent  │────▶│   Codebase   │
│ (pen.dev /   │     │ (Claude Code,│     │ (React/Vue/  │
│  Penpot)     │     │  Cursor,     │     │  Svelte)     │
│              │     │  Codex)      │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
  .pen files /         Reads design          Generates/
  Penpot tokens  ──▶   tokens/components  ──▶ updates
  Design library         + context              code
```

## Workflow Patterns

### Pattern 1: pen.dev + Claude Code (IDE-native)

**Prerequisites:**
- pen.dev extension in Cursor/VS Code
- `lib.pen` with design system primitives
- Claude Code / Cursor AI chat

**Workflow:**
```bash
# 1. Designer creates/updates lib.pen in IDE
# 2. Developer asks AI:
"Create a UserCard component using the Card and Button primitives from lib.pen.
Use the primary color token and md spacing."

# 3. AI reads lib.pen, generates:
#    - UserCard.tsx (React)
#    - UserCard.stories.tsx (Storybook)
#    - UserCard.test.tsx

# 4. Designer reviews in pen.dev canvas
# 5. Iterate: "Make the avatar slot larger" → AI updates .pen + code
```

**Key advantage:** Zero context switching. Design and code in same window.

### Pattern 2: Penpot + AI via API (Team/Collaborative)

**Prerequisites:**
- Self-hosted Penpot
- Design system library published
- Token export pipeline (JSON → codebase)
- AI agent with Penpot API access

**Workflow:**
```python
# AI agent script
import requests

# 1. Fetch design tokens from Penpot
tokens = requests.get(f"{PENPOT_URL}/api/design-tokens/{LIBRARY_ID}").json()

# 2. Fetch component definitions
components = requests.get(f"{PENPOT_URL}/api/components/{LIBRARY_ID}").json()

# 3. Generate code with full context
prompt = f"""
Design tokens: {json.dumps(tokens)}
Components: {json.dumps(components)}

Create a DashboardLayout component using:
- Grid primitive from design system
- Primary color token for header
- md/lg spacing tokens
- Card component for widgets
"""

# 4. AI generates code matching design system exactly
```

### Pattern 3: Hybrid (Best of Both)

| Phase | Tool | Why |
|---|---|---|
| **Design exploration** | Penpot (browser) | Real-time collab, stakeholder feedback |
| **Design system authoring** | Penpot | Token system, component library, versioning |
| **Token export** | Penpot → JSON/SCSS/CSS | Single source of truth |
| **AI development** | pen.dev (IDE) | AI reads `lib.pen`, generates code in-context |
| **Sync** | Git | Both `.pen` and exported tokens versioned |

## AI Prompt Engineering for Design-to-Code

### Good Prompt Structure
```
CONTEXT:
- Design system: [pen.dev lib.pen / Penpot exported tokens]
- Framework: React + TypeScript + Tailwind
- Component library: [list available primitives]

TASK:
Create [ComponentName] using:
- [Primitive1] for [purpose]
- [Token: color.primary] for [element]
- [Token: spacing.md] for [layout]

CONSTRAINTS:
- Must use existing primitives (no new tokens)
- Follow existing code patterns in /src/components
- Include Storybook story
- Accessible (ARIA)

EXAMPLE:
[Link to similar existing component]
```

### Anti-Patterns to Avoid
- ❌ "Create a nice button" → AI invents design
- ✅ "Create Button using Button primitive from lib.pen with primary color token"
- ❌ "Make it look modern" → Subjective, inconsistent
- ✅ "Match the Card component pattern from /src/components/Card.tsx"

## Integration with Our Stack

### SuperGuard Alarm Dashboard
1. **Design** in Penpot (self-hosted) → "SuperGuard Design System"
2. **Export tokens** → JSON → SuperGuard frontend build
3. **AI generates** React components using tokens
4. **pen.dev** for quick IDE iterations by developers

### Radio ArmsgeddonFM
1. **Design** admin UI in pen.dev (single developer)
2. **AI generates** Next.js dashboard components
3. **Tokens** in `.pen` = source of truth

### ParanoidX
1. **Penpot self-hosted** on sovereign infra
2. **Design system** for all ParanoidX UIs
3. **AI agents** query Penpot API for tokens

## Tooling Ecosystem (Aug 2026)

| Category | Tools |
|---|---|
| **IDE Design** | pen.dev (VS Code, Cursor) |
| **Web Design** | Penpot, Figma (with plugins) |
| **Token Management** | Style Dictionary, Tokens Studio, Penpot native |
| **AI Code Gen** | Claude Code, Cursor, Codex, Cline, Aider |
| **Design→Code** | Anima, Builder.io, Locofy, pen.dev native |
| **Storybook** | Auto-generated from design tokens |

## Challenges & Open Questions

1. **Token synchronization** — How to keep Penpot tokens ↔ pen.dev `lib.pen` in sync?
2. **AI hallucination** — Even with tokens, AI may compose incorrectly
3. **Versioning** — Design system semver vs code semver
4. **Designer ↔ Developer workflow** — Who owns the design system?
5. **Migration** — Existing Figma designs → Penpot/pen.dev

## Next Steps

- [ ] Set up pen.dev in Cursor + create `lib.pen` POC
- [ ] Deploy Penpot self-hosted + export tokens pipeline
- [ ] Build AI prompt templates for design-to-code
- [ ] Test: "Generate SuperGuard CameraCard from design tokens"
- [ ] Document chosen workflow in skill: `ai-design-to-code-workflow`
- [ ] Create GitHub Action: Penpot token change → PR with updated tokens

## References

- pen.dev docs: https://www.pen.dev/docs (AI Integration, Design Libraries)
- Penpot: https://penpot.app/features (Design Systems, Developer Handoff)
- midudev tweet: https://x.com/i/status/2086107198640300369
- Design Tokens W3C: https://tr.designtokens.org/
- Style Dictionary: https://amzn.github.io/style-dictionary/