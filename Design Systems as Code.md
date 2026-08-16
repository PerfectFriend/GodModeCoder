---
type: textbook-entry
topic: "Design Systems as Code (lib.pen / Penpot components)"
status: "🔴 Не изучено"
created: "2026-08-09"
tags: ["#textbook", "#design-systems", "#design-tokens", "#components"]
---

# Design Systems as Code — lib.pen & Penpot Components

> **Source:** pen.dev docs, Penpot features, tweet thread (Realta @astranua reply)

## The Concept

**Design Systems as Code** means design primitives (tokens, components, patterns) are defined in version-controlled files that both designers and developers (and AI) consume directly.

### pen.dev: `lib.pen` Files

From the tweet thread (Realta @astranua):
> "Puedes crear design systems (lib.pen) para crear los primitives de tu frontend, asi no se inventa un diseño de la nada sino que directamente busca el componente y lo usa en tu UI. Todo en el mismo repo"

**Translation:** "You can create design systems (lib.pen) to create frontend primitives, so AI doesn't invent designs from scratch but directly looks up the component and uses it in your UI. All in the same repo."

#### `lib.pen` Structure
```
lib.pen
├── variables (design tokens)
│   ├── colors: { primary, secondary, semantic... }
│   ├── spacing: { xs, sm, md, lg, xl... }
│   ├── typography: { font-families, scales, weights... }
│   └── border, shadow, radius...
├── components (primitives)
│   ├── Button (variants, sizes, states)
│   ├── Input, Select, Checkbox
│   ├── Card, Modal, Tooltip
│   └── Layout: Grid, Flex, Stack
├── slots (composition points)
└── patterns (composed components)
```

#### AI Workflow with `lib.pen`
1. Designer creates `lib.pen` with primitives
2. Developer imports `lib.pen` in codebase
3. AI (Claude Code, Cursor, Codex) reads `lib.pen`
4. AI generates components using exact tokens/components from library
5. **No hallucination** — AI uses defined primitives

### Penpot: Design Tokens + Component Libraries

#### Token System
```json
{
  "color": {
    "primary": { "value": "#0066CC", "type": "color" },
    "primary-hover": { "value": "#0052A3", "type": "color" }
  },
  "spacing": {
    "md": { "value": "16px", "type": "dimension" }
  },
  "typography": {
    "heading-1": { "value": { "fontFamily": "Inter", "fontSize": "32px", "fontWeight": "700" }, "type": "typography" }
  }
}
```

#### Export Formats
- **JSON** — for JS/TS consumption
- **SCSS** — `$color-primary: #0066CC;`
- **CSS Custom Properties** — `--color-primary: #0066CC;`
- **Tailwind Config** — `theme.extend.colors.primary`

#### Component Library
- Publish components to team library
- Versioned (semver)
- Consumable in other Penpot files
- Inspect → copy React/Vue/Svelte/HTML code

## Comparison: Design System Approaches

| Aspect | pen.dev `lib.pen` | Penpot Tokens | Figma Tokens | Storybook |
|---|---|---|---|---|
| **Format** | Proprietary text | JSON (open) | JSON (plugin) | Code (CSF) |
| **Version control** | ✅ Native Git | ✅ Native Git | Via plugin | ✅ Native Git |
| **AI readable** | ✅ Direct | ✅ JSON | Via API | Via code |
| **Designer edit** | In IDE | In browser | In Figma | Code only |
| **Self-hosted** | No | ✅ Full | No | ✅ |
| **Token sync** | Variables | Full system | Plugins | Manual |

## Integration Architecture for Our Stack

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Designers     │────▶│  pen.dev /       │────▶│   Design Tokens │
│  (in IDE/browser)│     │  Penpot          │     │  (JSON/SCSS/CSS)│
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   AI Agents     │◀───│  Codebase        │◀───▶│  Components     │
│  (Claude,       │     │  (React/Vue/     │     │  (mapped to     │
│   Cursor,       │     │   Svelte)        │     │   tokens)       │
│   Codex)        │     └──────────────────┘     └─────────────────┘
└─────────────────┘
```

## Implementation for SuperGuard/ParanoidX

### Option A: pen.dev (if team uses Cursor/VS Code)
1. Create `lib.pen` with SuperGuard UI primitives
2. Install pen.dev extension in all IDEs
3. AI agents read `lib.pen` → generate dashboard components

### Option B: Penpot (self-hosted, team collaboration)
1. Deploy Penpot on sovereign infra
2. Create "SuperGuard Design System" library
3. Export tokens → integrate into SuperGuard frontend build
4. AI queries Penpot API / reads exported JSON

### Hybrid Approach
- **Designers** use Penpot (browser, collaborative)
- **Developers** use pen.dev (IDE, AI workflow)
- **Tokens** exported from Penpot → consumed by pen.dev `lib.pen`

## Next Steps

- [ ] Evaluate: pen.dev vs Penpot for team workflow
- [ ] Create proof-of-concept `lib.pen` with 10 primitives
- [ ] Set up Penpot self-hosted + export tokens to JSON
- [ ] Build token pipeline: Penpot → JSON → frontend build
- [ ] Test AI generation: "Create Button component using design tokens"
- [ ] Document chosen approach in skill: `design-systems-as-code`

## References

- pen.dev docs: https://www.pen.dev/docs (Design Libraries, Variables)
- Penpot features: https://penpot.app/features (Design Systems, Tokens)
- Tweet thread: midudev + Realta reply (Aug 8 2026)
- Design Tokens W3C: https://tr.designtokens.org/