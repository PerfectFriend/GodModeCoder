#!/usr/bin/env python3
"""
DJ Pipeline for Radio ArmsgeddonFM
Integrates music generation, news/TTS, and audio mixing with ducking
"""

import os
import sys
import torch
import torchaudio
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import json
import time
import subprocess

sys.path.insert(0, "C:/Users/tomas/ai-radio")

from scripts.musicgen_cpu_client import MusicGenDirectML, RADIO_PRESETS, TIME_PRESET_MAP
from scripts.audio_stitcher import AudioStitcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DJPipeline:
    def __init__(
        self,
        music_dir: str = "C:/Users/tomas/ai-radio/music_output",
        news_dir: str = "C:/Users/tomas/ai-radio/newsfeed",
        output_dir: str = "C:/Users/tomas/ai-radio/radio_output",
        sample_rate: int = 32000,
    ):
        self.music_dir = Path(music_dir)
        self.news_dir = Path(news_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_rate = sample_rate

        self.music_gen = MusicGenDirectML(output_dir=str(self.music_dir))
        self.stitcher = AudioStitcher(sample_rate=sample_rate, output_dir=str(self.output_dir / "stitched"))

        self.duck_level = 0.15
        self.duck_fade_ms = 100

    def get_current_preset_name(self) -> str:
        hour = datetime.now().hour
        for (start, end), preset_name in TIME_PRESET_MAP.items():
            if start <= hour < end:
                return preset_name
        return "night"

    def ensure_music_for_preset(self, preset_name: str, target_minutes: int = 60) -> Path:
        preset_dir = self.music_dir / preset_name
        preset_dir.mkdir(parents=True, exist_ok=True)

        existing = list(preset_dir.glob("*.wav"))
        total_duration = 0
        for f in existing:
            try:
                info = torchaudio.info(str(f))
                total_duration += info.num_frames / info.sample_rate
            except:
                pass

        target_seconds = target_minutes * 60
        if total_duration >= target_seconds:
            logger.info(f"Preset {preset_name}: {total_duration/60:.1f}min available (need {target_minutes}min)")
            return preset_dir

        needed_minutes = int((target_seconds - total_duration) / 60) + 1
        segments_needed = (needed_minutes * 60) // 30 + 1

        logger.info(f"Generating {segments_needed} segments for {preset_name} ({needed_minutes}min needed)")
        paths = self.music_gen.generate_batch(
            count=segments_needed,
            preset_name=preset_name,
        )

        for p in paths:
            new_path = preset_dir / p.name
            p.rename(new_path)

        return preset_dir

    def create_hourly_music_track(self, preset_name: str) -> Path:
        preset_dir = self.ensure_music_for_preset(preset_name, target_minutes=65)

        output_name = f"hourly_{preset_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.wav"
        track_path = self.stitcher.create_hourly_track(
            str(preset_dir),
            preset_name,
            target_duration_minutes=60,
            output_name=output_name,
        )
        return track_path

    def load_music_track(self, path: Path) -> torch.Tensor:
        wav, sr = torchaudio.load(str(path))
        if sr != self.sample_rate:
            resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
            wav = resampler(wav)
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
        return wav

    def duck_music(self, music: torch.Tensor, speech: torch.Tensor, start_sample: int) -> torch.Tensor:
        music = music.clone()
        fade_samples = int(self.duck_fade_ms * self.sample_rate / 1000)
        speech_len = speech.shape[-1]
        end_sample = start_sample + speech_len

        start_sample = max(0, min(start_sample, music.shape[-1] - 1))
        end_sample = max(start_sample, min(end_sample, music.shape[-1]))

        duck_region_len = end_sample - start_sample
        if duck_region_len <= 0:
            return music

        envelope = torch.ones(duck_region_len)
        fade_in_len = min(fade_samples, duck_region_len // 2)
        fade_out_len = min(fade_samples, duck_region_len // 2)

        if fade_in_len > 0:
            envelope[:fade_in_len] = torch.linspace(1.0, self.duck_level, fade_in_len)
        if fade_out_len > 0:
            envelope[-fade_out_len:] = torch.linspace(self.duck_level, 1.0, fade_out_len)
        if duck_region_len > fade_in_len + fade_out_len:
            envelope[fade_in_len:-fade_out_len] = self.duck_level

        music[0, start_sample:end_sample] *= envelope
        return music

    def mix_news_into_music(
        self,
        music_path: Path,
        news_items: List[Dict],
        output_name: Optional[str] = None,
    ) -> Path:
        logger.info(f"Mixing {len(news_items)} news items into music")

        music = self.load_music_track(music_path)

        for item in news_items:
            audio_path = item.get("audio_path")
            offset_sec = item.get("offset_seconds", 0)

            if not audio_path or not Path(audio_path).exists():
                logger.warning(f"News audio not found: {audio_path}")
                continue

            speech, sr = torchaudio.load(str(audio_path))
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                speech = resampler(speech)
            if speech.shape[0] > 1:
                speech = speech.mean(dim=0, keepdim=True)

            start_sample = int(offset_sec * self.sample_rate)

            music = self.duck_music(music, speech, start_sample)

            end_sample = start_sample + speech.shape[-1]
            if end_sample <= music.shape[-1]:
                music[0, start_sample:end_sample] += speech[0]
            else:
                padding = end_sample - music.shape[-1]
                music = torch.cat([music, torch.zeros(1, padding)], dim=-1)
                music[0, start_sample:end_sample] += speech[0]

            logger.info(f"  Mixed news at {offset_sec:.1f}s ({speech.shape[-1]/self.sample_rate:.1f}s)")

        max_val = music.abs().max()
        if max_val > 0.95:
            music = music * (0.95 / max_val)
            logger.info(f"Normalized (peak was {max_val:.3f})")

        if output_name is None:
            output_name = f"mixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        output_path = self.output_dir / output_name
        torchaudio.save(str(output_path), music, self.sample_rate)
        duration = music.shape[-1] / self.sample_rate
        logger.info(f"Saved mixed track: {output_path} ({duration/60:.1f}min)")
        return output_path

    def generate_hourly_block(self, preset_name: Optional[str] = None) -> Dict[str, Any]:
        if preset_name is None:
            preset_name = self.get_current_preset_name()

        logger.info(f"=== Generating hourly block for {preset_name} ===")

        music_path = self.create_hourly_music_track(preset_name)
        news_items = self._load_news_for_hour(preset_name)
        mixed_path = self.mix_news_into_music(music_path, news_items)

        return {
            "preset": preset_name,
            "music_track": str(music_path),
            "mixed_track": str(mixed_path),
            "news_count": len(news_items),
            "timestamp": datetime.now().isoformat(),
        }

    def _load_news_for_hour(self, preset_name: str) -> List[Dict]:
        news_items = []
        logger.info("News loading not yet integrated - returning empty list")
        return news_items

    def run_continuous(self, interval_minutes: int = 60):
        logger.info(f"Starting continuous DJ pipeline (every {interval_minutes}min)")

        while True:
            try:
                result = self.generate_hourly_block()
                logger.info(f"Hourly block complete: {result}")
                self._send_telegram_report(result)
            except Exception as e:
                logger.error(f"Hourly generation failed: {e}", exc_info=True)
            time.sleep(interval_minutes * 60)

    def _send_telegram_report(self, result: Dict):
        try:
            msg = f"🎵 Radio ArmsgeddonFM - Hourly Block Generated\n"
            msg += f"Preset: {result['preset']}\n"
            msg += f"Music: {Path(result['music_track']).name}\n"
            msg += f"Mixed: {Path(result['mixed_track']).name}\n"
            msg += f"News items: {result['news_count']}\n"
            msg += f"Time: {result['timestamp']}"

            subprocess.run([
                "C:/Users/tomas/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe",
                "send", "--to", "telegram:143293811", msg
            ], capture_output=True, timeout=30)
        except Exception as e:
            logger.warning(f"Telegram report failed: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DJ Pipeline CLI")
    parser.add_argument("--preset", choices=list(RADIO_PRESETS.keys()), help="Force preset")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=60, help="Interval in minutes")
    parser.add_argument("--generate-music", action="store_true", help="Just generate music track")
    args = parser.parse_args()

    pipeline = DJPipeline()

    if args.continuous:
        pipeline.run_continuous(args.interval)
    elif args.generate_music:
        preset = args.preset or pipeline.get_current_preset_name()
        path = pipeline.create_hourly_music_track(preset)
        print(f"Generated: {path}")
    else:
        preset = args.preset or pipeline.get_current_preset_name()
        result = pipeline.generate_hourly_block(preset)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()