#!/usr/bin/env python3
"""
ACE-Step API Client for AI Radio
Replaces subprocess CLI calls with HTTP API to WSL2 GPU server.
Provides 20-40x speedup over CPU generation.
"""

import os
import sys
import time
import json
import requests
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import random

# ==================== CONFIGURATION ====================
API_BASE = os.environ.get("ACESTEP_API_URL", "http://localhost:8001")
API_KEY = os.environ.get("ACESTEP_API_KEY", "your-secret-radio-key")

RADIO_ROOT = r"C:\Users\tomas\ai-radio"
CACHE_DIR = os.path.join(RADIO_ROOT, "cache")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# ==================== DATA CLASSES ====================
@dataclass
class GenerationParams:
    """Mirrors ACE-Step GenerationParams for API"""
    task_type: str = "text2music"
    caption: str = ""
    lyrics: str = "[Instrumental]"
    instrumental: bool = True
    duration: float = -1.0
    bpm: Optional[int] = None
    keyscale: str = ""
    timesignature: str = ""
    vocal_language: str = "unknown"
    inference_steps: int = 8
    shift: float = 3.0
    infer_method: str = "ode"
    seed: int = -1
    guidance_scale: float = 7.0
    use_adg: bool = False
    audio_cover_strength: float = 1.0
    thinking: bool = True
    lm_temperature: float = 0.85
    lm_cfg_scale: float = 2.0
    use_cot_metas: bool = True
    use_cot_caption: bool = True
    use_cot_language: bool = True
    use_constrained_decoding: bool = True
    batch_size: int = 1
    audio_format: str = "wav"

@dataclass
class GenerationResult:
    task_id: str
    status: int  # 0=queued, 1=success, 2=failed
    audio_paths: List[str]
    seeds: List[int]
    metas: Dict
    error: Optional[str] = None

# ==================== CORE API FUNCTIONS ====================
def release_task(params: GenerationParams) -> str:
    """Submit generation task, return task_id"""
    payload = {
        "prompt": params.caption,
        "lyrics": params.lyrics,
        "thinking": params.thinking,
        "audio_duration": params.duration if params.duration > 0 else None,
        "bpm": params.bpm,
        "keyscale": params.keyscale or None,
        "timesignature": params.timesignature or None,
        "vocal_language": params.vocal_language,
        "inference_steps": params.inference_steps,
        "shift": params.shift,
        "infer_method": params.infer_method,
        "seed": params.seed if params.seed > 0 else None,
        "batch_size": params.batch_size,
        "audio_format": params.audio_format,
        "guidance_scale": params.guidance_scale,
        "use_adg": params.use_adg,
        "lm_temperature": params.lm_temperature,
        "lm_cfg_scale": params.lm_cfg_scale,
        "use_cot_metas": params.use_cot_metas,
        "use_cot_caption": params.use_cot_caption,
        "use_cot_language": params.use_cot_language,
    }
    
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    r = requests.post(
        f"{API_BASE}/release_task",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    r.raise_for_status()
    return r.json()["data"]["task_id"]


def poll_task(task_id: str, poll_interval: float = 1.0, timeout: int = 600) -> Dict:
    """Poll task until completion, return result dict"""
    start = time.time()
    while time.time() - start < timeout:
        r = requests.post(
            f"{API_BASE}/query_result",
            headers=HEADERS,
            json={"task_id_list": [task_id]},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()["data"][0]
        status = data["status"]
        
        if status == 1:  # success
            return json.loads(data["result"])[0]
        elif status == 2:  # failed
            raise Exception(f"Generation failed: {data.get('error', 'Unknown error')}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Task {task_id} timed out after {timeout}s")


def download_audio(audio_url: str, local_path: str) -> str:
    """Download generated audio file"""
    full_url = f"{API_BASE}{audio_url}" if audio_url.startswith("/") else audio_url
    r = requests.get(full_url, stream=True, timeout=60)
    r.raise_for_status()
    
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return local_path


def generate_batch(params: GenerationParams, out_dir: str, count: int = 1) -> List[GenerationResult]:
    """Generate multiple variations, return list of results with local paths"""
    results = []
    
    for i in range(count):
        # Use random seed for variety unless specified
        if params.seed == -1:
            params.seed = random.randint(1, 2**31 - 1)
        elif count > 1:
            params.seed += 1  # sequential seeds
        
        print(f"[{i+1}/{count}] Generating (seed={params.seed})...")
        
        # 1. Submit
        task_id = release_task(params)
        print(f"  Task ID: {task_id}")
        
        # 2. Poll
        result = poll_task(task_id)
        
        # 3. Download
        audio_url = result["file"]
        local_path = os.path.join(out_dir, f"{params.task_type}_{task_id[:8]}.wav")
        download_audio(audio_url, local_path)
        
        # Parse seeds from result
        seed_str = result.get("seed_value", str(params.seed))
        seeds = [int(s) for s in seed_str.split(",")]
        
        gen_result = GenerationResult(
            task_id=task_id,
            status=1,
            audio_paths=[local_path],
            seeds=seeds,
            metas=result.get("metas", {})
        )
        results.append(gen_result)
        print(f"  ✅ Saved: {local_path}")
        print(f"  Metas: BPM={gen_result.metas.get('bpm')}, Key={gen_result.metas.get('keyscale')}, Dur={gen_result.metas.get('duration')}s")
    
    return results


def select_best_by_score(results: List[GenerationResult]) -> GenerationResult:
    """Select best result by quality score (if available)"""
    # For now, return first - extend with quality scoring when available
    return results[0]


# ==================== PRESET LOADER ====================
def load_preset(preset_name: str) -> GenerationParams:
    """Load a preset TOML and convert to GenerationParams"""
    preset_path = os.path.join(RADIO_ROOT, "scripts", "presets", f"{preset_name}.toml")
    
    if not os.path.exists(preset_path):
        raise FileNotFoundError(f"Preset not found: {preset_path}")
    
    # Simple TOML parsing (for flat key=value files)
    params = GenerationParams()
    with open(preset_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"')
                
                # Type conversion
                if hasattr(params, key):
                    field_type = type(getattr(params, key))
                    if field_type == bool:
                        value = value.lower() in ("true", "1", "yes")
                    elif field_type == int:
                        value = int(value) if value else None
                    elif field_type == float:
                        value = float(value) if value else None
                    elif field_type == Optional[int]:
                        value = int(value) if value and value != "None" else None
                    setattr(params, key, value)
    
    return params


# ==================== PRESET DEFINITIONS ====================
PRESETS = {
    # Jingles
    "jingle_morning": GenerationParams(
        caption="short radio jingle, bright morning energy, brass fanfare, upbeat major key, catchy 3-note motif, station identification, professional broadcast quality, 5 seconds",
        duration=5, bpm=140, keyscale="C Major", timesignature="4",
        lm_temperature=0.85
    ),
    "jingle_night": GenerationParams(
        caption="late night radio jingle, dreamy atmospheric, soft synth pads, gentle chime melody, intimate whisper-quiet, starry night vibe, 8 seconds",
        duration=8, bpm=80, keyscale="F Major", timesignature="4",
        lm_temperature=0.75
    ),
    "jingle_breaking": GenerationParams(
        caption="breaking news jingle, urgent dramatic, orchestral stab, tension-building, brass and timpani, authoritative, immediate attention-grabber, 4 seconds",
        duration=4, bpm=120, keyscale="D Minor", timesignature="4",
        lm_temperature=0.7
    ),
    
    # Beds
    "bed_news": GenerationParams(
        caption="radio news bed, neutral underscore, subtle pulsating texture, minimal melody, steady unobtrusive rhythm, professional broadcast bed, loopable, 45 seconds",
        duration=45, bpm=100, keyscale="C Major", timesignature="4",
        lm_temperature=0.7
    ),
    "bed_talk": GenerationParams(
        caption="talk show bed, warm intimate, soft acoustic guitar fingerpicking, light percussion, conversational pace, friendly supportive atmosphere, loopable, 60 seconds",
        duration=60, bpm=90, keyscale="G Major", timesignature="4",
        lm_temperature=0.8
    ),
    "bed_music": GenerationParams(
        caption="music show bed, groovy electronic, subtle four-on-floor, filtered synth bass, atmospheric pads, club-ready but unobtrusive, loopable, 45 seconds",
        duration=45, bpm=124, keyscale="A Minor", timesignature="4",
        lm_temperature=0.85
    ),
    "bed_late_night": GenerationParams(
        caption="late night ambient bed, dreamy chillout, slow evolving pads, sparse piano motifs, minimal percussion, intimate star-gazing atmosphere, loopable, 90 seconds",
        duration=90, bpm=65, keyscale="Eb Major", timesignature="4",
        lm_temperature=0.75
    ),
    
    # Full Tracks
    "track_rock": GenerationParams(
        caption="full radio rock track, energetic classic rock, driving drums, electric guitar riffs, powerful bass, catchy chorus hook, structured verse-chorus-bridge, professional production, radio edit, 3 minutes",
        duration=180, bpm=136, keyscale="E Minor", timesignature="4",
        lm_temperature=0.85
    ),
    "track_pop": GenerationParams(
        caption="radio pop hit, upbeat contemporary pop, polished production, synthesizer hooks, four-on-floor beat, infectious chorus, verse-pre-chorus-chorus structure, radio-friendly, 2:30 minutes",
        duration=150, bpm=122, keyscale="C Major", timesignature="4",
        lm_temperature=0.85
    ),
    "track_electronic": GenerationParams(
        caption="electronic dance music track, progressive house, driving bassline, euphoric breakdown, hands-in-the-air climax, DJ-friendly intro/outro, festival energy, 4 minutes",
        duration=240, bpm=126, keyscale="F# Minor", timesignature="4",
        lm_temperature=0.9
    ),
    "track_ambient": GenerationParams(
        caption="ambient soundscape, slow evolving textures, ethereal pads, subtle field recordings, meditative, no drums, beatless, deep listening, 5 minutes",
        duration=300, bpm=50, keyscale="D Major", timesignature="4",
        shift=2.5, lm_temperature=0.8
    ),
    "track_jazz": GenerationParams(
        caption="smooth jazz radio track, relaxed cool jazz, walking bass, brushed drums, piano comping, saxophone lead, intimate club atmosphere, sophisticated, 3 minutes",
        duration=180, bpm=100, keyscale="Bb Major", timesignature="4",
        lm_temperature=0.8
    ),
    "track_chiptune": GenerationParams(
        caption="chiptune retro gaming, 8-bit nostalgia, square wave leads, arpeggiated bass, fast tempo, playful energetic, authentic NES/Sega sound, 2 minutes",
        duration=120, bpm=160, keyscale="C Major", timesignature="4",
        lm_temperature=0.9
    ),
    
    # Ads
    "ad_energetic": GenerationParams(
        caption="radio commercial bed, high energy, punchy rhythmic, driving percussion, confident brass stabs, urgent call-to-action feel, 20 seconds",
        duration=20, bpm=140, keyscale="G Major", timesignature="4",
        lm_temperature=0.75
    ),
    "ad_relaxed": GenerationParams(
        caption="radio ad bed, warm friendly, soft acoustic, gentle pace, trustworthy sincere tone, local business feel, 30 seconds",
        duration=30, bpm=85, keyscale="D Major", timesignature="4",
        lm_temperature=0.7
    ),
    
    # News Intros
    "news_intro_main": GenerationParams(
        caption="main news intro, authoritative orchestral, brass fanfare, timpani roll, serious important tone, broadcast standard, 6 seconds",
        duration=6, bpm=110, keyscale="C Major", timesignature="4",
        lm_temperature=0.65
    ),
    "news_intro_sports": GenerationParams(
        caption="sports news intro, energetic dynamic, brass and percussion, victorious triumphant, stadium atmosphere, 5 seconds",
        duration=5, bpm=130, keyscale="D Major", timesignature="4",
        lm_temperature=0.75
    ),
    "news_intro_weather": GenerationParams(
        caption="weather forecast intro, calm breezy, light mallets, airy pads, gentle informative, 4 seconds",
        duration=4, bpm=90, keyscale="F Major", timesignature="4",
        lm_temperature=0.7
    ),
    "news_intro_tech": GenerationParams(
        caption="tech news intro, futuristic electronic, glitchy synth, digital atmosphere, innovative forward-looking, 5 seconds",
        duration=5, bpm=120, keyscale="E Minor", timesignature="4",
        lm_temperature=0.8
    ),
    
    # Sweepers
    "sweeper_up": GenerationParams(
        caption="radio sweeper up, rising energy, pitch-up sweep, white noise riser, impact hit, transition to high energy, 3 seconds",
        duration=3, bpm=128, keyscale="", timesignature="4",
        lm_temperature=0.7
    ),
    "sweeper_down": GenerationParams(
        caption="radio sweeper down, falling energy, pitch-down sweep, sub drop, transition to calm, 3 seconds",
        duration=3, bpm=80, keyscale="", timesignature="4",
        lm_temperature=0.7
    ),
}

# ==================== HIGH-LEVEL GENERATION FUNCTIONS ====================
def generate_by_preset(preset_name: str, out_dir: str, count: int = 1, **overrides) -> List[str]:
    """Generate audio using a named preset with optional parameter overrides"""
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESETS.keys())}")
    
    params = PRESETS[preset_name]
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(params, key):
            setattr(params, key, value)
    
    results = generate_batch(params, out_dir, count)
    return [r.audio_paths[0] for r in results]


def generate_jingle(style: str, out_dir: str, count: int = 3) -> List[str]:
    """Generate jingles of specified style"""
    preset_map = {
        "morning": "jingle_morning",
        "night": "jingle_night", 
        "breaking": "jingle_breaking",
    }
    preset = preset_map.get(style, "jingle_morning")
    return generate_by_preset(preset, out_dir, count)


def generate_bed(category: str, out_dir: str, count: int = 2) -> List[str]:
    """Generate beds for voiceover"""
    preset_map = {
        "news": "bed_news",
        "talk": "bed_talk",
        "music": "bed_music",
        "late_night": "bed_late_night",
    }
    preset = preset_map.get(category, "bed_news")
    return generate_by_preset(preset, out_dir, count)


def generate_music_track(style: str, out_dir: str, count: int = 2) -> List[str]:
    """Generate full music tracks"""
    preset_map = {
        "rock": "track_rock",
        "pop": "track_pop",
        "electronic": "track_electronic",
        "ambient": "track_ambient",
        "jazz": "track_jazz",
        "chiptune": "track_chiptune",
    }
    preset = preset_map.get(style, "track_pop")
    return generate_by_preset(preset, out_dir, count)


def generate_ad(style: str, out_dir: str, count: int = 3) -> List[str]:
    """Generate ad beds"""
    preset_map = {
        "energetic": "ad_energetic",
        "relaxed": "ad_relaxed",
    }
    preset = preset_map.get(style, "ad_energetic")
    return generate_by_preset(preset, out_dir, count)


def generate_news_intro(category: str, out_dir: str) -> str:
    """Generate news category intro"""
    preset_map = {
        "main": "news_intro_main",
        "sports": "news_intro_sports",
        "weather": "news_intro_weather",
        "tech": "news_intro_tech",
    }
    preset = preset_map.get(category, "news_intro_main")
    return generate_by_preset(preset, out_dir, 1)[0]


def generate_sweeper(direction: str, out_dir: str) -> str:
    """Generate transition sweeper"""
    preset = "sweeper_up" if direction == "up" else "sweeper_down"
    return generate_by_preset(preset, out_dir, 1)[0]


# ==================== HEALTH CHECK ====================
def check_api_health() -> bool:
    """Verify API server is reachable"""
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.status_code == 200
    except:
        return False


# ==================== CLI ====================
def main():
    parser = argparse.ArgumentParser(description="ACE-Step API Client for AI Radio")
    parser.add_argument("--preset", help="Preset name (see PRESETS dict)")
    parser.add_argument("--style", help="Style shortcut (jingle/bed/track/ad/news/sweeper)")
    parser.add_argument("--category", help="Category within style")
    parser.add_argument("--out-dir", default=CACHE_DIR, help="Output directory")
    parser.add_argument("--count", type=int, default=1, help="Number of variations")
    parser.add_argument("--duration", type=float, help="Override duration (seconds)")
    parser.add_argument("--bpm", type=int, help="Override BPM")
    parser.add_argument("--seed", type=int, help="Fixed seed")
    parser.add_argument("--list-presets", action="store_true", help="List available presets")
    parser.add_argument("--health-check", action="store_true", help="Check API server")
    
    args = parser.parse_args()
    
    if args.health_check:
        ok = check_api_health()
        print(f"API Server ({API_BASE}): {'✅ OK' if ok else '❌ FAIL'}")
        sys.exit(0 if ok else 1)
    
    if args.list_presets:
        print("Available presets:")
        for name in sorted(PRESETS.keys()):
            print(f"  {name}")
        sys.exit(0)
    
    if not check_api_health():
        print(f"❌ API server not reachable at {API_BASE}")
        print("Start WSL2 server: python -m acestep.api_server --port 8001 --host 0.0.0.0")
        sys.exit(1)
    
    # Determine preset
    if args.preset:
        preset_name = args.preset
    elif args.style:
        if args.style == "jingle":
            preset_name = f"jingle_{args.category or 'morning'}"
        elif args.style == "bed":
            preset_name = f"bed_{args.category or 'news'}"
        elif args.style == "track":
            preset_name = f"track_{args.category or 'pop'}"
        elif args.style == "ad":
            preset_name = f"ad_{args.category or 'energetic'}"
        elif args.style == "news":
            preset_name = f"news_intro_{args.category or 'main'}"
        elif args.style == "sweeper":
            preset_name = f"sweeper_{args.category or 'up'}"
        else:
            print(f"Unknown style: {args.style}")
            sys.exit(1)
    else:
        print("Specify --preset or --style")
        sys.exit(1)
    
    # Build overrides
    overrides = {}
    if args.duration:
        overrides["duration"] = args.duration
    if args.bpm:
        overrides["bpm"] = args.bpm
    if args.seed:
        overrides["seed"] = args.seed
    
    # Generate
    try:
        paths = generate_by_preset(preset_name, args.out_dir, args.count, **overrides)
        print(f"\n✅ Generated {len(paths)} files:")
        for p in paths:
            print(f"  {p}")
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()