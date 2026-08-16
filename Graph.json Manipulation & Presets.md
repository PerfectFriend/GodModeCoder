Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, obsidian, graph-json, presets, graph-view, automation, plugin-development]
source: textbook
status: learned
date: 2026-08-10
priority: 9
---

# Graph.json Manipulation & Presets

## Summary
Obsidian stores Graph View settings in `.obsidian/graph.json`. This file contains all visual parameters (filters, colors, groups, forces) and can be programmatically manipulated to create **presets**, **automated view switching**, and **dynamic graph configurations** synced with external systems (GodModeCoder, Radio, Paranoidx).

## Core Structure: graph.json

### Location
```
C:\Vault\.obsidian\graph.json
```

### Schema (Key Fields)
```json
{
  "collapse-filter": true,
  "search": "",
  "showTags": false,
  "showAttachments": false,
  "hideUnresolved": false,
  "showOrphans": true,
  "colorGroups": [
    {
      "query": "tag:#project",
      "color": { "a": 1, "r": 230, "g": 126, "b": 34 },
      "opacity": 1
    }
  ],
  "forceLayout": {
    "chargeStrength": -30,
    "linkStrength": 0.7,
    "linkDistance": 30,
    "centerStrength": 0.1
  },
  "filters": {
    "tags": ["#project", "#agent"],
    "folders": [],
    "attachments": false,
    "unresolved": false,
    "orphans": true
  },
  "groups": {
    "tag:#type/human": { "color": "#f39c12" },
    "tag:#type/agent": { "color": "#3498db" }
  }
}
```

## Preset System

### Native Presets (Obsidian 1.5+)
Obsidian now supports **Graph Presets** natively:
1. Configure graph view → Click preset dropdown → "Save as preset"
2. Presets stored in `.obsidian/graph-presets.json`
3. Switch via Graph View toolbar or command palette

### Programmatic Preset Management

#### 1. Save Current View as Preset
```python
# scripts/save_graph_preset.py
import json
from pathlib import Path

VAULT = Path(r"C:\Vault")
GRAPH_JSON = VAULT / ".obsidian" / "graph.json"
PRESETS_FILE = VAULT / ".obsidian" / "graph-presets.json"

def save_preset(name, description=""):
    graph_config = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    presets = json.loads(PRESETS_FILE.read_text(encoding="utf-8")) if PRESETS_FILE.exists() else {}
    
    presets[name] = {
        "name": name,
        "description": description,
        "options": graph_config,
        "created": "2026-08-10T00:00:00Z"
    }
    
    PRESETS_FILE.write_text(json.dumps(presets, indent=2, ensure_ascii=False))
    print(f"Saved preset: {name}")

# Usage
save_preset("evolution-alive", "Only alive evolution nodes")
save_preset("radio-pipeline", "Radio ArmsgeddonFM pipeline stages")
save_preset("paranoidx-containers", "5-container sovereign stack")
```

#### 2. Load Preset (Apply to Graph View)
```python
# scripts/load_graph_preset.py
import json
import subprocess
from pathlib import Path

VAULT = Path(r"C:\Vault")
GRAPH_JSON = VAULT / ".obsidian" / "graph.json"
PRESETS_FILE = VAULT / ".obsidian" / "graph-presets.json"

def load_preset(name):
    presets = json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
    if name not in presets:
        raise ValueError(f"Preset '{name}' not found")
    
    # Update graph.json
    GRAPH_JSON.write_text(json.dumps(presets[name]["options"], indent=2, ensure_ascii=False))
    
    # Trigger Obsidian reload (via URI or restart)
    # obsidian://graph?preset=name  (if supported)
    print(f"Loaded preset: {name}")

# Usage
load_preset("evolution-alive")
```

#### 3. Preset Definitions (JSON)
```json
{
  "evolution-alive": {
    "name": "evolution-alive",
    "description": "Only alive evolution nodes with fitness colors",
    "options": {
      "search": "tag:#evolution AND tag:#status/alive",
      "colorGroups": [
        {"query": "tag:#type/human", "color": {"r":243,"g":156,"b":18}, "opacity":1},
        {"query": "tag:#type/agent", "color": {"r":52,"g":152,"b":219}, "opacity":1},
        {"query": "tag:#type/pipeline", "color": {"r":155,"g":89,"b":182}, "opacity":1}
      ],
      "forceLayout": {"chargeStrength": -40, "linkStrength": 0.8, "linkDistance": 40}
    }
  },
  "radio-pipeline": {
    "name": "radio-pipeline",
    "description": "Radio pipeline stages with memory types",
    "options": {
      "search": "tag:#radio",
      "colorGroups": [
        {"query": "tag:#stage/generation", "color": {"r":52,"g":152,"b":219}},
        {"query": "tag:#stage/mixing", "color": {"r":155,"g":89,"b":182}},
        {"query": "tag:#stage/evaluation", "color": {"r":243,"g":156,"b":18}},
        {"query": "tag:#stage/consolidation", "color": {"r":46,"g":204,"b":113}}
      ]
    }
  }
}
```

## Dynamic Graph Configuration (Real-time)

### 1. Sync from External System (GodModeCoder)
```python
# scripts/sync_graph_from_godmodecoder.py
import yaml, json
from pathlib import Path

GRAPH_YAML = Path(r"C:\Users\yusya\GodModeCoder\configs\graph.yaml")
GRAPH_JSON = Path(r"C:\Vault\.obsidian\graph.json")

def generate_color_groups(nodes):
    """Generate colorGroups from node types"""
    type_colors = {
        "human": (243, 156, 18),
        "agent": (52, 152, 219),
        "pipeline": (155, 89, 182),
        "radio": (231, 76, 60),
        "optimizer": (46, 204, 113),
        "watchdog": (230, 126, 34)
    }
    groups = []
    for ntype, (r,g,b) in type_colors.items():
        groups.append({
            "query": f"tag:#type/{ntype}",
            "color": {"r": r, "g": g, "b": b},
            "opacity": 1
        })
    return groups

def generate_search_filter(nodes):
    """Build search query from node statuses"""
    statuses = set(n.get("status", "unknown") for n in nodes)
    if "alive" in statuses and len(statuses) == 1:
        return "tag:#status/alive"
    return " OR ".join(f"tag:#status/{s}" for s in statuses)

def sync():
    graph = yaml.safe_load(GRAPH_YAML.read_text(encoding="utf-8"))
    nodes = graph.get("nodes", [])
    
    current = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    
    # Update only dynamic parts
    current["colorGroups"] = generate_color_groups(nodes)
    current["search"] = generate_search_filter(nodes)
    
    # Preserve user layout settings
    # current["forceLayout"] = current.get("forceLayout", {...})
    
    GRAPH_JSON.write_text(json.dumps(current, indent=2, ensure_ascii=False))
    print(f"Synced {len(nodes)} nodes to graph.json")

if __name__ == "__main__":
    sync()
```

### 2. Auto-Switch Preset on Context (Obsidian URI)
```markdown
<!-- In dashboard notes -->
[Open Evolution Graph](obsidian://graph?preset=evolution-alive)
[Open Radio Pipeline](obsidian://graph?preset=radio-pipeline)
[Open Paranoidx Stack](obsidian://graph?preset=paranoidx-containers)
```

## Graph Presets Plugin (Community)

### Installation
```bash
cd C:\Vault\.obsidian\plugins
git clone https://github.com/Sphinxes0o0/graph-presets.git graph-presets
cd graph-presets && npm install && npm run build
```

### Features
- **Preset UI** in Graph View toolbar
- **Auto-save** on view change
- **Keyboard shortcuts** for preset switching
- **Import/Export** presets as JSON files
- **Per-folder presets** (context-aware)

### Configuration (plugin manifest)
```json
{
  "id": "graph-presets",
  "name": "Graph Presets",
  "version": "1.0.0",
  "minAppVersion": "1.5.0",
  "description": "Save and load Graph View presets with UI",
  "author": "Sphinxes0o0",
  "isDesktopOnly": false
}
```

## Integration Patterns

### 1. Nightly Evolution → Graph Update
```python
# In autonomous_evolution.py after COMMIT phase
def update_graph_after_evolution():
    # 1. Sync Graph.yaml → graph.json colors/search
    subprocess.run(["python", "scripts/sync_graph_from_godmodecoder.py"])
    
    # 2. Create timestamped preset
    subprocess.run(["python", "scripts/save_graph_preset.py", 
                   f"evolution-gen-{cycle}", f"Generation {cycle} snapshot"])
    
    # 3. Notify via Obsidian URI (optional)
    # obsidian://graph?preset=evolution-gen-5
```

### 2. Radio Pipeline Stage → Graph Focus
```python
# In Radio pipeline when stage changes
def on_stage_change(stage):
    preset_map = {
        "generation": "radio-generation",
        "mixing": "radio-mixing",
        "evaluation": "radio-evaluation",
        "consolidation": "radio-consolidation"
    }
    if stage in preset_map:
        subprocess.run(["python", "scripts/load_graph_preset.py", preset_map[stage]])
```

### 3. Paranoidx Container Health → Graph Alert
```python
# When container health changes
def on_container_health(container, status):
    current = json.loads(GRAPH_JSON.read_text())
    
    # Update color group for this container type
    for group in current["colorGroups"]:
        if container in group["query"]:
            if status == "healthy":
                group["color"] = {"r": 46, "g": 204, "b": 113}  # Green
            elif status == "degraded":
                group["color"] = {"r": 243, "g": 156, "b": 18}  # Orange
            else:
                group["color"] = {"r": 231, "g": 76, "b": 60}   # Red
    
    GRAPH_JSON.write_text(json.dumps(current, indent=2))
```

## Backup & Versioning

```bash
# Daily backup of graph configs
cp C:\Vault\.obsidian\graph.json C:\Vault\Backups\graph\graph-$(date +%Y%m%d).json
cp C:\Vault\.obsidian\graph-presets.json C:\Vault\Backups\graph\presets-$(date +%Y%m%d).json

# Git tracking (in vault)
cd C:\Vault && git add .obsidian/graph.json .obsidian/graph-presets.json && git commit -m "graph: update presets $(date)"
```

## Best Practices

| Practice | Why |
|----------|-----|
| Separate static/dynamic config | Preserve user layout (forceLayout) while syncing colors |
| Version presets with timestamps | Rollback to known-good views |
| Use tag-based queries | Stable across file moves/renames |
| Limit colorGroups to ≤10 | Performance & visual clarity |
| Document preset purpose | Team onboarding, future debugging |

## References
- Obsidian Forum: [Graph View Presets](https://forum.obsidian.md/t/graph-view-presets-to-save-and-load-filters-display-settings/8131)
- Graph Presets Plugin: https://github.com/Sphinxes0o0/graph-presets
- Obsidian URI Scheme: https://help.obsidian.md/Advanced+topics/Obsidian+URI
- Graph.json Schema: Reverse-engineered from `.obsidian/graph.json`