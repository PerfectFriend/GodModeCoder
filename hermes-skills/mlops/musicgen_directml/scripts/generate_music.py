#!/usr/bin/env python3
"""
MusicGen CPU Generation Script for Radio ArmsgeddonFM
Generates 30-second music segments and stitches them into hourly blocks.
Run on CPU (DirectML operators incomplete on Windows).
"""

import torch
import torchaudio
import numpy as np
from pathlib import Path
from audiocraft.models import MusicGen
import time

# Model path (downloaded via hf-mirror.com)
MODEL_DIR = Path("C:/Users/tomas/ai-radio/models/musicgen-small")
OUTPUT_DIR = Path("C:/Users/tomas/ai-radio/music/generated")
BLOCKS_DIR = Path("C:/Users/tomas/ai-radio/music/background")

# Radio presets by time of day
RADIO_PRESETS = {
    "morning": "upbeat electronic, 110 bpm, energetic, synthesizers, optimistic",
    "day_chill": "chill lo-fi hip hop, 85 bpm, relaxed, jazz samples, background",
    "day_ambient": "ambient electronic, 90 bpm, atmospheric, soft pads, minimal",
    "evening_synthwave": "synthwave, 100 bpm, nostalgic, retro, analog synthesizers",
    "night_ambient": "dark ambient, 60 bpm, minimal, drone, deep bass, meditative",
    "late_night_drone": "drone ambient, 50 bpm, very slow, sub-bass, hypnotic",
    "transition": "short transition sting, 5 seconds, electronic, smooth, radio jingle",
}

# Generation params
GEN_PARAMS = {
    "duration": 30,
    "top_k": 250,
    "top_p": 0.9,
    "temperature": 1.0,
    "cfg_coef": 3.0,
}

def load_model():
    """Load MusicGen-small on CPU."""
    print(f"Loading model from {MODEL_DIR}...")
    model = MusicGen.get_pretrained(str(MODEL_DIR), device='cpu')
    model.set_generation_params(**GEN_PARAMS)
    print(f"Model loaded. Sample rate: {model.sample_rate}")
    return model

def generate_segment(model, prompt, progress=False):
    """Generate a single 30-second segment."""
    with torch.no_grad():
        wav = model.generate([prompt], progress=progress)
    return wav[0].cpu()

def crossfade(a, b, crossfade_samples):
    """Crossfade between two audio tensors."""
    if len(a) <= crossfade_samples or len(b) <= crossfade_samples:
        return torch.cat([a, b])
    
    fade_out = torch.linspace(1.0, 0.0, crossfade_samples)
    fade_in = torch.linspace(0.0, 1.0, crossfade_samples)
    
    a_end = a[-crossfade_samples:] * fade_out
    b_start = b[:crossfade_samples] * fade_in
    crossed = a_end + b_start
    
    return torch.cat([a[:-crossfade_samples], crossed, b[crossfade_samples:]])

def stitch_segments(segments, crossfade_ms, sample_rate):
    """Stitch multiple segments with crossfade."""
    crossfade_samples = int(sample_rate * crossfade_ms / 1000)
    result = segments[0]
    for seg in segments[1:]:
        result = crossfade(result, seg, crossfade_samples)
    return result

def generate_hour_block(preset_name, output_path, crossfade_ms=500):
    """Generate 1-hour block (120 x 30 sec segments)."""
    if preset_name not in RADIO_PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    prompt = RADIO_PRESETS[preset_name]
    print(f"Generating 1-hour block for '{preset_name}' ({prompt})")
    
    model = load_model()
    segments = []
    
    for i in range(120):
        if i % 10 == 0:
            print(f"  Segment {i+1}/120...")
        wav = generate_segment(model, prompt, progress=(i == 0))
        segments.append(wav)
    
    print("  Stitching with crossfade...")
    crossfade_samples = int(model.sample_rate * crossfade_ms / 1000)
    full = stitch_segments(segments, crossfade_ms, model.sample_rate)
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torchaudio.save(str(output_path), full.unsqueeze(0), model.sample_rate)
    duration = len(full) / model.sample_rate
    print(f"  Saved: {output_path} ({duration:.1f} sec)")
    return output_path

def generate_daily_schedule():
    """Generate full 24-hour schedule."""
    schedule = [
        ("late_night_drone", "00", 4),   # 00:00-04:00
        ("late_night_drone", "04", 2),   # 04:00-06:00
        ("morning", "06", 4),            # 06:00-10:00
        ("day_chill", "10", 3),          # 10:00-13:00
        ("day_ambient", "13", 4),        # 13:00-17:00
        ("evening_synthwave", "17", 4),  # 17:00-21:00
        ("night_ambient", "21", 3),      # 21:00-00:00
    ]
    
    BLOCKS_DIR.mkdir(parents=True, exist_ok=True)
    
    for preset, start_hour, hours in schedule:
        for h in range(hours):
            hour = (int(start_hour) + h) % 24
            output = BLOCKS_DIR / f"{hour:02d}_{preset}.wav"
            if not output.exists():
                print(f"\n=== Generating {hour:02d}:00 ({preset}) ===")
                generate_hour_block(preset, output)
            else:
                print(f"Skipping {output} (exists)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_music.py segment <preset> [output.wav]")
        print("  python generate_music.py hour <preset> [output.wav]")
        print("  python generate_music.py daily")
        print("\nPresets:", ", ".join(RADIO_PRESETS.keys()))
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "segment":
        preset = sys.argv[2] if len(sys.argv) > 2 else "day_chill"
        output = sys.argv[3] if len(sys.argv) > 3 else f"segment_{preset}_{int(time.time())}.wav"
        model = load_model()
        wav = generate_segment(model, RADIO_PRESETS[preset], progress=True)
        torchaudio.save(output, wav.unsqueeze(0), model.sample_rate)
        print(f"Saved: {output}")
    
    elif cmd == "hour":
        preset = sys.argv[2] if len(sys.argv) > 2 else "day_chill"
        output = sys.argv[3] if len(sys.argv) > 3 else f"hour_{preset}_{int(time.time())}.wav"
        generate_hour_block(preset, output)
    
    elif cmd == "daily":
        generate_daily_schedule()
    
    else:
        print(f"Unknown command: {cmd}")