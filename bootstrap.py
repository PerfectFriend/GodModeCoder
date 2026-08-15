#!/usr/bin/env python3
"""
GodModeCoder — Bootstrap installer for new machine
Run: python bootstrap.py
"""
import subprocess
import sys
import os
from pathlib import Path

def run(cmd, desc):
    print(f"\n🔧 {desc}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FAILED: {desc}")
        print(result.stderr)
        return False
    print(f"✅ {desc}")
    return True

def main():
    print("=" * 60)
    print("  GodModeCoder — Bootstrap Installer")
    print("=" * 60)
    
    # 1. Python packages
    if not run("pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    # 2. Ollama
    if not run("winget install Ollama.Ollama --accept-source-agreements", "Installing Ollama via winget"):
        print("⚠️  Ollama install failed - install manually from ollama.com")
    
    # 3. Pull qwen3:8b model
    if not run("ollama pull qwen3:8b", "Pulling qwen3:8b model"):
        print("⚠️  Model pull failed - run 'ollama pull qwen3:8b' manually")
    
    # 4. Obsidian
    if not run("winget install Obsidian.Obsidian --accept-source-agreements", "Installing Obsidian"):
        print("⚠️  Obsidian install failed - install manually")
    
    # 5. Configure Ollama CPU-only
    print("\n🔧 Configuring Ollama CPU-only mode...")
    env_vars = {
        "OLLAMA_NUM_GPU": "0",
        "OLLAMA_GPU_LAYERS": "0",
        "OLLAMA_FLASH_ATTENTION": "0",
        "OLLAMA_KV_CACHE_TYPE": "f16",
        "OLLAMA_NO_VULKAN": "1",
        "OLLAMA_CUDA": "0",
        "OLLAMA_ROCM": "0",
        "OLLAMA_METAL": "0",
        "OLLAMA_LOW_VRAM": "1",
        "OLLAMA_NUMA": "true",
    }
    for key, value in env_vars.items():
        subprocess.run(f"setx {key} {value}", shell=True)
    
    # 6. Create cron jobs (Windows Task Scheduler via cronjob skill)
    print("\n⏰ Setting up cron jobs...")
    cron_jobs = [
        ("graph-pulse-export", "every 6h", "export_graph_to_vault.py", ["obsidian-graph-engineering"]),
        ("textbook-learning", "every 6h", "textbook_learn.py", ["obsidian-graph-engineering"]),
    ]
    for name, schedule, script, skills in cron_jobs:
        cmd = f'hermes cron create --name "{name}" --schedule "{schedule}" --script "{script}" --skills {skills}'
        run(cmd, f"Creating cron job: {name}")
    
    print("\n" + "=" * 60)
    print("✅ Bootstrap complete!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Open Obsidian → Open vault: C:\\Vault")
    print("2. Enable Dataview plugin (Community plugins → Dataview → Enable)")
    print("3. Enable JavaScript queries in Dataview settings")
    print("4. Run: python scripts/hermes-verify-all.py")
    print("5. Test Ollama: ollama run qwen3:8b 'привет'")
    print("\n🧬 GodModeCoder is ready to evolve!")

if __name__ == "__main__":
    main()