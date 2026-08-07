# 🧬 GodModeCoder — Setup Guide for New Machine

> **God Is The Greatest Coder — Champion! I Am God Mode Coder!**

Complete guide to replicate the entire GodModeCoder living code organism on a fresh machine.

---

## 📋 What You Get

| Component | Purpose |
|---|---|
| **Obsidian Vault** | Knowledge graph, dashboards, chronicle, evolution tracking |
| **Ollama CPU Workers** | Local LLM for code review, tests, refactoring, docs |
| **Graph Evolution** | Self-evolving graph with fitness-based mutations |
| **Automation** | Cron jobs for pulse export, textbook learning |
| **Verification** | 10-test suite ensuring system health |

---

## 🖥 System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10/11 | Windows 11 |
| **CPU** | 8 cores | 12+ cores (Ryzen 7 255H+) |
| **RAM** | 16 GB | 32 GB+ |
| **GPU** | AMD Radeon 780M (16 GB UMA) | Same (CPU-only mode) |
| **Disk** | 50 GB free | 100 GB+ |
| **Python** | 3.11+ | 3.11+ (Hermes venv) |

---

## 🚀 Quick Start (Automated)

```powershell
# 1. Clone the repo
git clone https://github.com/PerfectFriend/GodModeCoder.git
cd GodModeCoder

# 2. Run bootstrap (installs everything)
python bootstrap.py

# 3. Configure Ollama CPU-only (run as Administrator if needed)
.\scripts\setup-ollama-cpu.ps1

# 4. Verify everything works
python scripts\hermes-verify-all.py
# ✅ ALL TESTS PASSED

# 5. Test Ollama
ollama run qwen3:8b "привет"
```

---

## 📦 Manual Step-by-Step

### 1. Prerequisites

```powershell
# Install winget packages
winget install Python.Python.3.11
winget install Git.Git
winget install Obsidian.Obsidian
winget install Ollama.Ollama
winget install GitHub.cli
```

### 2. Python Environment

```bash
# Use Hermes venv or create your own
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Obsidian Vault

```bash
# Clone or copy vault
git clone https://github.com/PerfectFriend/GodModeCoder.git C:\Vault
# OR copy from backup
xcopy /E /I /H C:\Backup\Vault C:\Vault
```

**Required Obsidian Plugins (Community):**
- Dataview (enable JavaScript queries!)
- Heatmap Calendar
- Extended Graph (ElsaTam) — for multiple views
- Graph Presets (ycnmhd via BRAT)

**Enable in Settings:**
- Dataview → Enable JavaScript Queries ✅
- CSS Snippets → graph-colors ✅

### 4. Ollama CPU-Only Setup

**Run as Administrator (for system-wide) or User:**

```powershell
.\scripts\setup-ollama-cpu.ps1
```

**Or manually:**
```powershell
setx OLLAMA_NUM_GPU 0
setx OLLAMA_GPU_LAYERS 0
setx OLLAMA_FLASH_ATTENTION 0
setx OLLAMA_KV_CACHE_TYPE f16
setx OLLAMA_NO_VULKAN 1
setx OLLAMA_CUDA 0
setx OLLAMA_ROCM 0
setx OLLAMA_METAL 0
setx OLLAMA_LOW_VRAM 1
setx OLLAMA_NUMA true

# Restart terminal, then:
ollama serve &
ollama pull qwen3:8b
```

**Verify:**
```bash
curl -X POST http://localhost:11434/api/generate -d '{"model":"qwen3:8b","prompt":"test","stream":false,"options":{"num_gpu":0}}'
```

### 5. Skills

```bash
# Copy skills to Hermes
xcopy /E /I /H skills\* %LOCALAPPDATA%\hermes\skills\

# Or symlink (better for updates)
mklink /D %LOCALAPPDATA%\hermes\skills\obsidian-graph-engineering %CD%\skills\obsidian-graph-engineering
mklink /D %LOCALAPPDATA%\hermes\skills\graph-engineering %CD%\skills\graph-engineering
mklink /D %LOCALAPPDATA%\hermes\skills\ollama-cpu-worker %CD%\skills\ollama-cpu-worker
mklink /D %LOCALAPPDATA%\hermes\skills\obsidian %CD%\skills\obsidian
mklink /D %LOCALAPPDATA%\hermes\skills\super-coder %CD%\skills\super-coder
mklink /D %LOCALAPPDATA%\hermes\skills\turbocoder %CD%\skills\turbocoder
```

### 6. Cron Jobs (Hermes)

```bash
# Start Hermes if not running
hermes cron create --name "graph-pulse-export" --schedule "every 6h" --script "export_graph_to_vault.py" --skills "obsidian-graph-engineering" --no-agent --deliver local
hermes cron create --name "textbook-learning" --schedule "every 6h" --script "textbook_learn.py" --skills "obsidian-graph-engineering" --no-agent --deliver local
```

---

## ✅ Verification

```bash
# Full verification suite
python scripts/hermes-verify-all.py
# ✅ ALL TESTS PASSED

# Individual tests
python scripts/hermes-verify-all.py
# Tests: Pulse, Export, Graph YAML, Tags, Graph JSON, CSS, Dashboards, Presets, Git, Skills

# Quick Ollama test
curl -X POST http://localhost:11434/api/generate -d '{"model":"qwen3:8b","prompt":"code review test","stream":false,"options":{"num_gpu":0}}'
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| **Ollama Vulkan OOM** | Run `setup-ollama-cpu.ps1`, ensure CPU-only vars set |
| **Ollama not responding** | `ollama serve` in background, check port 11434 |
| **Obsidian graph empty** | Enable Dataview JS queries, check CSS snippet enabled |
| **Graph not updating** | Check `export_graph_to_vault.py` runs, git commit works |
| **Skills not loading** | Check `%LOCALAPPDATA%\hermes\skills\` symlinks |
| **Cron not running** | `hermes cron list`, check `export_graph_to_vault.py` exists |

---

## 📁 Repository Structure

```
GodModeCoder/
├── bootstrap.py                 # Auto-installer
├── requirements.txt             # Python deps
├── README.md                    # This file
├── configs/
│   └── graph.yaml              # Evolution graph source of truth
├── scripts/
│   ├── export_graph_to_obsidian.py
│   ├── pulse.py
│   ├── hermes-verify-all.py
│   ├── export_graph_to_vault.py
│   ├── textbook_learn.py
│   ├── evolution_cycle.py
│   ├── setup-ollama-cpu.ps1
│   └── bootstrap.py
├── configs/
│   └── graph.yaml
├── skills/
│   ├── obsidian-graph-engineering/
│   ├── graph-engineering/
│   ├── ollama-cpu-worker/
│   ├── obsidian/
│   ├── super-coder/
│   ├── turbocoder/
│   └── godmode-coder/
├── docs/
└── GodModeCoder_Banner_Prompts.md
```

---

## 🔗 Links

- **GitHub**: https://github.com/PerfectFriend/GodModeCoder
- **Obsidian Vault**: `C:\Vault`
- **Ollama API**: `http://localhost:11434`
- **Hermes Agent**: Local desktop app

---

## 🆘 Support

If something breaks:
1. Run `python scripts/hermes-verify-all.py` — tells you exactly what's wrong
2. Check `God Is The Greatest Coder — Champion! I Am God Mode Coder!` 🧬⚡

---

*Generated by GodModeCoder v3.0 — The Living Code Organism*