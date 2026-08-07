#!/usr/bin/env python3
"""
Procedural Music Generation for Radio ArmsgeddonFM
Zero-dependency, instant CPU synthesis (FM, additive, noise-based).
Production fallback when ML models fail on Windows/AMD.
"""

import numpy as np
from scipy.io import wavfile
from scipy import signal
from pathlib import Path
from typing import Callable, Dict
import time


# ============================================================
# Core Synthesis Engines
# ============================================================

def fm_synth(duration=30, sr=44100, carrier_freq=220, mod_ratio=2.0, mod_index=5.0,
             env_attack=0.1, env_decay=0.3, env_sustain=0.5, env_release=1.0) -> np.ndarray:
    """FM synthesis — bell/pad tones, metallic timbres."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    modulator = np.sin(2 * np.pi * carrier_freq * mod_ratio * t)
    carrier = np.sin(2 * np.pi * carrier_freq * t + mod_index * modulator)
    
    # ADSR envelope
    env = np.ones_like(t)
    attack_samples = int(env_attack * sr)
    decay_samples = int(env_decay * sr)
    release_samples = int(env_release * sr)
    sustain_start = attack_samples + decay_samples
    sustain_end = len(t) - release_samples
    
    env[:attack_samples] = np.linspace(0, 1, attack_samples)
    env[attack_samples:sustain_start] = np.linspace(1, env_sustain, decay_samples)
    env[sustain_start:sustain_end] = env_sustain
    env[sustain_end:] = np.linspace(env_sustain, 0, release_samples)
    
    return carrier * env


def additive_synth(duration=30, sr=44100, fundamental=110, harmonics=None,
                   env_attack=0.5, env_release=2.0) -> np.ndarray:
    """Additive synthesis — organ/pad textures, harmonic stacks."""
    if harmonics is None:
        harmonics = [(1, 1.0), (2, 0.5), (3, 0.33), (4, 0.25), (5, 0.2)]
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    sig = np.zeros_like(t)
    for h, amp in harmonics:
        sig += amp * np.sin(2 * np.pi * fundamental * h * t)
    
    # Slow attack/release envelope
    env = np.ones_like(t)
    attack = int(env_attack * sr)
    release = int(env_release * sr)
    env[:attack] = np.linspace(0, 1, attack)**2
    env[-release:] = np.linspace(1, 0, release)**2
    return sig * env / sum(abs(amp) for _, amp in harmonics)


def noise_based(duration=30, sr=44100, noise_type='pink',
                filter_cutoff=2000, resonance=2.0, env_attack=0.01, env_release=0.5) -> np.ndarray:
    """Filtered noise — percussive, wind, rain, vinyl crackle textures."""
    n = int(sr * duration)
    if noise_type == 'white':
        noise = np.random.normal(0, 1, n)
    elif noise_type == 'pink':
        # Voss-McCartney pink noise approximation
        rows = 16
        array = np.random.normal(0, 1, (rows, n))
        noise = np.sum(array, axis=0) / rows
    elif noise_type == 'brown':
        noise = np.cumsum(np.random.normal(0, 1, n))
        noise = noise / (np.max(np.abs(noise)) + 1e-10)
    else:
        noise = np.random.normal(0, 1, n)
    
    # Resonant lowpass
    b, a = signal.butter(2, filter_cutoff / (sr/2), btype='low')
    filtered = signal.filtfilt(b, a, noise)
    
    # Envelope
    env = np.ones(n)
    attack = int(env_attack * sr)
    release = int(env_release * sr)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    return filtered * env


def supersaw(duration=30, sr=44100, fundamental=110, detune=0.01, num_osc=7,
             env_attack=0.1, env_release=1.0) -> np.ndarray:
    """Supersaw — trance/pads, wide stereo-ready (mono here)."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    sig = np.zeros_like(t)
    for i in range(num_osc):
        freq = fundamental * (1 + detune * (i - num_osc//2) * 0.1)
        # Sawtooth via additive (odd harmonics)
        for h in range(1, 10, 2):
            sig += (1/h) * np.sin(2 * np.pi * freq * h * t)
    
    env = np.ones_like(t)
    attack = int(env_attack * sr)
    release = int(env_release * sr)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    return sig * env / (num_osc * 5)


# ============================================================
# Radio Presets — Parameterized for Time-of-Day
# ============================================================

RADIO_PRESETS_PROCEDURAL: Dict[str, Callable[[], np.ndarray]] = {
    "morning": lambda: (
        0.7 * fm_synth(30, 44100, carrier_freq=220, mod_ratio=2.0, mod_index=3,
                       env_attack=0.05, env_decay=0.2, env_sustain=0.7, env_release=0.5) +
        0.3 * additive_synth(30, 44100, fundamental=110, 
                            harmonics=[(1,1),(2,0.5),(3,0.3),(5,0.15)],
                            env_attack=0.3, env_release=1.0)
    ),
    "day_chill": lambda: (
        0.75 * additive_synth(30, 44100, fundamental=146, 
                             harmonics=[(1,1),(2,0.4),(3,0.25),(4,0.15),(6,0.1)],
                             env_attack=0.5, env_release=2.0) +
        0.25 * noise_based(30, 44100, 'pink', filter_cutoff=3000, env_attack=0.01, env_release=1.0)
    ),
    "evening_synthwave": lambda: (
        0.8 * fm_synth(30, 44100, carrier_freq=110, mod_ratio=1.5, mod_index=8,
                       env_attack=0.1, env_decay=0.3, env_sustain=0.6, env_release=1.0) +
        0.2 * supersaw(30, 44100, fundamental=110, detune=0.02, num_osc=5)
    ),
    "night_ambient": lambda: (
        0.85 * additive_synth(30, 44100, fundamental=55, 
                             harmonics=[(1,1),(2,0.6),(3,0.4),(4,0.2),(5,0.15)],
                             env_attack=2.0, env_release=5.0) +
        0.15 * noise_based(30, 44100, 'brown', filter_cutoff=800, env_attack=0.5, env_release=3.0)
    ),
    "late_night_drone": lambda: (
        0.9 * additive_synth(30, 44100, fundamental=41, 
                            harmonics=[(1,1),(2,0.7),(3,0.5),(4,0.3)],
                            env_attack=5.0, env_release=10.0) +
        0.1 * noise_based(30, 44100, 'pink', filter_cutoff=400, env_attack=1.0, env_release=5.0)
    ),
}


# ============================================================
# Block Generation — Seamless Hour+ Loops
# ============================================================

def generate_hour_block(preset: str, duration_sec: int = 3600, sr: int = 44100) -> np.ndarray:
    """Generate 1-hour seamless block from 30-sec procedural loops with crossfade."""
    if preset not in RADIO_PRESETS_PROCEDURAL:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(RADIO_PRESETS_PROCEDURAL.keys())}")
    
    chunk_fn = RADIO_PRESETS_PROCEDURAL[preset]
    chunk_duration = 30
    num_chunks = duration_sec // chunk_duration
    chunks = []
    
    for i in range(num_chunks):
        chunk = chunk_fn()
        # Add subtle variation per chunk (prevents mechanical repetition)
        if i > 0:
            chunk = chunk * (0.95 + 0.1 * np.random.random())
        chunks.append(chunk)
    
    # Crossfade between chunks (500ms)
    crossfade = int(0.5 * sr)
    result = chunks[0].copy()
    for chunk in chunks[1:]:
        result[-crossfade:] *= np.linspace(1, 0, crossfade)
        chunk[:crossfade] *= np.linspace(0, 1, crossfade)
        result = np.concatenate([result[:-crossfade], 
                                 result[-crossfade:] + chunk[:crossfade], 
                                 chunk[crossfade:]])
    
    return result[:duration_sec * sr]


def save_wav(audio: np.ndarray, path: str, sr: int = 44100):
    """Save normalized float32 audio to 16-bit WAV."""
    audio = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(path, sr, audio_int16)


# ============================================================
# CLI / Direct Usage
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Procedural Radio Music Generator")
    parser.add_argument("--preset", choices=list(RADIO_PRESETS_PROCEDURAL.keys()), default="night_ambient")
    parser.add_argument("--duration", type=int, default=1800, help="Duration in seconds (default 30 min)")
    parser.add_argument("--output", default="output/music", help="Output directory")
    parser.add_argument("--sr", type=int, default=44100, help="Sample rate")
    args = parser.parse_args()
    
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {args.preset} block: {args.duration}s @ {args.sr}Hz...")
    start = time.time()
    
    audio = generate_hour_block(args.preset, args.duration, args.sr)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{args.preset}_{timestamp}_{args.duration}s.wav"
    filepath = out_dir / filename
    
    save_wav(audio, str(filepath), args.sr)
    
    elapsed = time.time() - start
    print(f"✅ Done in {elapsed:.2f}s: {filepath}")
    print(f"   Size: {filepath.stat().st_size / 1024 / 1024:.1f} MB")