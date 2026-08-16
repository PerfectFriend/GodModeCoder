Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, obsidian, css-snippets, graph-view, node-styling, theming]
source: textbook
status: learned
date: 2026-08-10
priority: 9
---

# CSS Snippets Override Graph Colors

## Summary
Obsidian's Graph View can be fully customized via **CSS Snippets** (`.obsidian/snippets/*.css`). Nodes and edges receive CSS classes based on tags, frontmatter, and link types, enabling semantic coloring without plugins.

## Core Mechanism

### 1. Graph View DOM Structure
```html
<div class="graph-view">
  <svg class="graph">
    <g class="nodes">
      <g class="node" data-name="My Note">
        <circle class="color-fill" r="8"></circle>
        <text>My Note</text>
      </g>
    </g>
    <g class="links">
      <line class="link" source="A" target="B"></line>
    </g>
  </svg>
</div>
```

### 2. Automatic CSS Classes
Obsidian adds classes based on metadata:
| Selector | Source | Example |
|----------|--------|---------|
| `.node[data-name="..."]` | Filename | Always present |
| `.node.tag-<tag>` | `#tag` in file | `.tag-project`, `.tag-agent` |
| `.node.color-<color>` | `cssclasses: [color-red]` in frontmatter | `.color-red` |
| `.link[source="..."][target="..."]` | Wikilink connection | Always present |

### 3. Snippet Loading
1. Create `C:\Vault\.obsidian\snippets\graph-colors.css`
2. Settings → Appearance → CSS Snippets → Enable `graph-colors`
3. Changes apply instantly (hot-reload)

## Node Coloring Strategies

### Strategy A: By Tag (Most Common)
```css
/* .obsidian/snippets/graph-by-tag.css */

/* Base node style */
.graph-view .node .color-fill {
  fill: var(--text-muted); /* default gray */
  stroke: var(--background-primary);
  stroke-width: 1.5px;
}

/* Project nodes — orange */
.graph-view .node.tag-project .color-fill {
  fill: #e67e22;
}

/* Agent nodes — blue */
.graph-view .node.tag-agent .color-fill {
  fill: #3498db;
}

/* Human nodes — green */
.graph-view .node.tag-human .color-fill {
  fill: #2ecc71;
}

/* Pipeline nodes — purple */
.graph-view .node.tag-pipeline .color-fill {
  fill: #9b59b6;
}

/* Radio nodes — red */
.graph-view .node.tag-radio .color-fill {
  fill: #e74c3c;
}

/* Dormant/Dead nodes — dimmed */
.graph-view .node.tag-dormant .color-fill,
.graph-view .node.tag-dead .color-fill {
  fill: #95a5a6;
  opacity: 0.5;
}

/* Hover highlight */
.graph-view .node:hover .color-fill {
  stroke: var(--text-normal);
  stroke-width: 3px;
  filter: brightness(1.2);
}
```

### Strategy B: By Frontmatter `cssclasses`
```yaml
---
cssclasses: [color-red, size-large]
---
```
```css
.graph-view .node.color-red .color-fill { fill: #e74c3c; }
.graph-view .node.color-blue .color-fill { fill: #3498db; }
.graph-view .node.color-green .color-fill { fill: #2ecc71; }
.graph-view .node.color-purple .color-fill { fill: #9b59b6; }
.graph-view .node.color-orange .color-fill { fill: #e67e22; }

.graph-view .node.size-large { transform: scale(1.3); }
.graph-view .node.size-small { transform: scale(0.7); }
```

### Strategy C: By Status (Alive/Dead/Dormant)
```css
.graph-view .node.status-alive .color-fill { fill: #2ecc71; }
.graph-view .node.status-dormant .color-fill { fill: #f39c12; opacity: 0.7; }
.graph-view .node.status-dead .color-fill { fill: #e74c3c; opacity: 0.4; }
.graph-view .node.status-unknown .color-fill { fill: #95a5a6; }
```

## Edge (Link) Styling

```css
/* .obsidian/snippets/graph-edges.css */

/* Default edge */
.graph-view .link {
  stroke: var(--text-muted);
  stroke-opacity: 0.3;
  stroke-width: 1px;
}

/* Typed edges (if Graph Link Types plugin or manual classes) */
.graph-view .
C:\Vault\CSS Snippets Override Graph Colors.md


link.edge-type-depends_on { stroke: #e74c3c; stroke-width: 2px; }
.graph-view .link.edge-type-related { stroke: #3498db; stroke-width: 1.5px; }
.graph-view .link.edge-type-blocks { stroke: #f39c12; stroke-dasharray: 5,5; }
.graph-view .link.edge-type-triggers { stroke: #2ecc71; stroke-width: 2px; }

/* Hover edge highlight */
.graph-view .link:hover {
  stroke: var(--text-normal);
  stroke-opacity: 1;
  stroke-width: 3px;
}
```

## Advanced: Dynamic Sizing by Metadata

```css
/* Size by connection count (requires JS to add class) */
/* Use DataviewJS to add .degree-<n> class */

/* Size by fitness score (0-100) */
.graph-view .node.fitness-high .color-fill { r: 12; } /* via JS */
.graph-view .node.fitness-medium .color-fill { r: 8; }
.graph-view .node.fitness-low .color-fill { r: 5; }

/* Pulse animation for active nodes */
@keyframes pulse {
  0% { filter: brightness(1); }
  50% { filter: brightness(1.5); }
  100% { filter: brightness(1); }
}
.graph-view .node.active .color-fill {
  animation: pulse 2s infinite;
}
```

## Integration with Our Systems

### 1. GodModeCoder Evolution Graph Colors
```css
/* .obsidian/snippets/godmodecoder-graph.css */

/* Type colors */
.graph-view .node.type-human .color-fill { fill: #f39c12; }      /* Orange */
.graph-view .node.type-agent .color-fill { fill: #3498db; }      /* Blue */
.graph-view .node.type-pipeline .color-fill { fill: #9b59b6; }   /* Purple */
.graph-view .node.type-radio .color-fill { fill: #e74c3c; }      /* Red */
.graph-view .node.type-optimizer .color-fill { fill: #2ecc71; }  /* Green */
.graph-view .node.type-watchdog .color-fill { fill: #e67e22; }   /* Dark orange */

/* Status colors */
.graph-view .node.status-alive .color-fill { fill: #2ecc71; }
.graph-view .node.status-dormant .color-fill { fill: #f39c12; opacity: 0.6; }
.graph-view .node.status-dead .color-fill { fill: #e74c3c; opacity: 0.3; }

/* Fitness ring (via JS adding border) */
.graph-view .node.fitness-pass { stroke: #2ecc71; stroke-width: 3px; }
.graph-view .node.fitness-fail { stroke: #e74c3c; stroke-width: 3px; }
```

### 2. Radio ArmsgeddonFM Pipeline
```css
.graph-view .node.stage-generation .color-fill { fill: #3498db; }
.graph-view .node.stage-mixing .color-fill { fill: #9b59b6; }
.graph-view .node.stage-evaluation .color-fill { fill: #f39c12; }
.graph-view .node.stage-consolidation .color-fill { fill: #2ecc71; }
.graph-view .node.stage-backup .color-fill { fill: #e67e22; }

/* Memory type indicators */
.graph-view .node.memory-semantic .color-fill { stroke: #3498db; stroke-width: 2px; }
.graph-view .node.memory-procedural .color-fill { stroke: #9b59b6; stroke-width: 2px; }
.graph-view .node.memory-episodic .color-fill { stroke: #2ecc71; stroke-width: 2px; }
```

### 3. Paranoidx Sovereign Stack
```css
.graph-view .node.container-smp .color-fill { fill: #1abc9c; }
.graph-view .node.container-coturn .color-fill { fill: #3498db; }
.graph-view .node.container-v2ray .color-fill { fill: #9b59b6; }
.graph-view .node.container-tor .color-fill { fill: #e74c3c; }
.graph-view .node.container-xftp .color-fill { fill: #f39c12; }

.graph-view .node.security-high .color-fill { stroke: #e74c3c; stroke-width: 3px; }
.graph-view .node.license-gate .color-fill { stroke: #f39c12; stroke-dasharray: 3,3; }
```

## Automation: Tag → CSS Class Sync

```python
# scripts/sync_tags_to_css.py
# Reads all tags from vault, generates CSS snippet

import re
from pathlib import Path

VAULT = Path(r"C:\Vault")
SNIPPET = VAULT / ".obsidian" / "snippets" / "auto-tag-colors.css"

# Predefined color palette (HSL for harmony)
PALETTE = [
    (12, 85%, 55%),   # Orange
    (210, 85%, 55%),  # Blue
    (140, 65%, 45%),  # Green
    (270, 65%, 55%),  # Purple
    (0, 75%, 55%),    # Red
    (45, 90%, 55%),   # Yellow
    (30, 85%, 55%),   # Amber
    (180, 65%, 45%),  # Teal
]

def extract_all_tags():
    tags = set()
    for md in VAULT.rglob("*.md"):
        if md.name.startswith("."): continue
        content = md.read_text(encoding="utf-8", errors="ignore")
        # Frontmatter tags
        if content.startswith("---"):
            fm_end = content.find("---", 3)
            if fm_end > 0:
                fm = content[3:fm_end]
                for line in fm.split("\n"):
                    if line.strip().startswith("tags:"):
                        tags.update(re.findall(r'#?(\w[\w-]*)', line))
        # Inline tags
        tags.update(re.findall(r'#(\w[\w-]*)', content))
    return sorted(tags)

def generate_css(tags):
    css = ["/* AUTO-GENERATED: Tag colors */", ""]
    css.append(".graph-view .node .color-fill {")
    css.append("  fill: var(--text-muted);")
    css.append("  stroke: var(--background-primary);")
    css.append("  stroke-width: 1.5px;")
    css.append("}")
    css.append("")
    
    for i, tag in enumerate(tags):
        h, s, l = PALETTE[i % len(PALETTE)]
        css.append(f".graph-view .node.tag-{tag} .color-fill {{")
        css.append(f"  fill: hsl({h}, {s}%, {l}%);")
        css.append("}")
    return "\n".join(css)

tags = extract_all_tags()
css = generate_css(tags)
SNIPPET.write_text(css, encoding="utf-8")
print(f"Generated {len(tags)} tag colors in {SNIPPET}")
```

## Best Practices

| Practice | Why |
|----------|-----|
| Use `tag-<name>` classes | Automatic from `#tag`, no JS needed |
| Define fallback `.color-fill` | Un-tagged nodes stay visible |
| Keep specificity low | Avoid `!important`, let cascade work |
| Use HSL palette | Easy to generate harmonious colors |
| Separate snippets by domain | `graph-godmodecoder.css`, `graph-radio.css` |
| Test in both themes | Light/Dark mode may need adjustments |

## References
- Obsidian Forum: [Graph View Node Colors](https://forum.obsidian.md/t/is-there-a-way-to-change-the-color-of-the-nodes-in-graph-view/8271)
- Obsidian Forum: [Tags as Graph CSS Classes](https://forum.obsidian.md/t/provide-tags-as-graph-css-classes-attributes-to-allow-coloring-of-graph-nodes/6300)
- CSS Snippets Docs: https://help.obsidian.md/Extending+Obsidian/CSS+snippets