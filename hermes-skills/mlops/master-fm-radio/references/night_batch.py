#!/usr/bin/env python3
"""
Master-FM: NIGHT BATCH (20:00-07:00).
Full generation of all content: music, news, ads, jingles, audiobooks.
Runs via cron at 20:00.
"""
import os
import sys
import time
import yaml
import subprocess

RADIO_ROOT = r"C:\Users\tomas\ai-radio"
CONFIG_PATH = os.path.join(RADIO_ROOT, "config.yaml")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["radio"]


def run_script(script_name, args=None, timeout=1800):
    """Run generation script with timeout."""
    script_path = os.path.join(RADIO_ROOT, "scripts", script_name)
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    print(f"[night_batch] Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            print(f"[night_batch] ERROR ({script_name}): {result.stderr[-500:]}")
            return False
        else:
            print(f"[night_batch] OK: {script_name}")
            return True
    except subprocess.TimeoutExpired:
        print(f"[night_batch] TIMEOUT: {script_name}")
        return False
    except Exception as e:
        print(f"[night_batch] EXCEPTION: {script_name}: {e}")
        return False


def main():
    cfg = load_config()
    night = cfg["modes"]["night_batch"]

    if not night["enabled"]:
        print("[night_batch] Night batch disabled in config")
        return

    print(f"[night_batch] ===== NIGHT BATCH START ({time.strftime('%H:%M:%S')}) =====")
    start = time.time()

    # 1. MUSIC (all styles)
    if night["generate_music"]:
        print("[night_batch] --- Generating music ---")
        run_script("gen_music.py", ["--all", "--count", str(night["music_per_style"]), "--duration", str(night["music_duration_sec"])], timeout=3600)

    # 2. NEWS
    if night["generate_news"]:
        print("[night_batch] --- Generating news ---")
        run_script("gen_voice_content.py", timeout=600)

    # 3. ADS
    if night["generate_ads"]:
        print("[night_batch] --- Generating ads ---")
        # Ads included in gen_voice_content.py

    # 4. JINGLES
    if night["generate_jingles"]:
        print("[night_batch] --- Generating jingles ---")
        # Jingles included in gen_voice_content.py

    # 5. AUDIOBOOKS
    if night["generate_audiobooks"]:
        print("[night_batch] --- Generating audiobooks ---")
        # TODO: add gen_audiobook.py when ACE-Step supports long-form

    elapsed = time.time() - start
    print(f"[night_batch] ===== NIGHT BATCH DONE in {elapsed:.0f}s =====")


if __name__ == "__main__":
    main()