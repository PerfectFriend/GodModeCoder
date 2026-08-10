#!/usr/bin/env python3
"""
Audio Stitcher for Radio ArmsgeddonFM
Combines multiple music segments into continuous tracks with crossfade
"""

import os
import torch
import torchaudio
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AudioStitcher:
    def __init__(
        self,
        crossfade_duration: float = 2.0,
        sample_rate: int = 32000,
        output_dir: str = "C:/Users/tomas/ai-radio/music_output/stitched",
    ):
        self.crossfade_duration = crossfade_duration
        self.crossfade_samples = int(crossfade_duration * sample_rate)
        self.sample_rate = sample_rate
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_audio(self, path: str) -> torch.Tensor:
        wav, sr = torchaudio.load(path)
        if sr != self.sample_rate:
            resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
            wav = resampler(wav)
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
        return wav

    def crossfade(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        fade_len = min(self.crossfade_samples, a.shape[-1] // 2, b.shape[-1] // 2)
        if fade_len <= 0:
            return torch.cat([a, b], dim=-1)

        fade_out = torch.linspace(1.0, 0.0, fade_len)
        fade_in = torch.linspace(0.0, 1.0, fade_len)

        a_end = a[..., -fade_len:] * fade_out
        b_start = b[..., :fade_len] * fade_in
        crossfaded = a_end + b_start

        result = torch.cat([
            a[..., :-fade_len],
            crossfaded,
            b[..., fade_len:],
        ], dim=-1)

        return result

    def stitch_files(
        self,
        file_paths: List[str],
        output_name: Optional[str] = None,
    ) -> Path:
        if not file_paths:
            raise ValueError("No files provided")

        logger.info(f"Stitching {len(file_paths)} files...")

        result = self.load_audio(file_paths[0])
        logger.info(f"  Base: {file_paths[0]} ({result.shape[-1]/self.sample_rate:.1f}s)")

        for i, path in enumerate(file_paths[1:], 1):
            next_audio = self.load_audio(path)
            logger.info(f"  Adding: {path} ({next_audio.shape[-1]/self.sample_rate:.1f}s)")
            result = self.crossfade(result, next_audio)

        if output_name is None:
            from datetime import datetime
            output_name = f"stitched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        output_path = self.output_dir / output_name
        torchaudio.save(str(output_path), result, self.sample_rate)
        duration = result.shape[-1] / self.sample_rate
        logger.info(f"Saved: {output_path} ({duration:.1f}s, {duration/60:.1f}min)")
        return output_path

    def create_hourly_track(
        self,
        segment_dir: str,
        preset_name: str,
        target_duration_minutes: int = 60,
        output_name: Optional[str] = None,
    ) -> Path:
        segment_dir = Path(segment_dir)
        segments = sorted(segment_dir.glob(f"*{preset_name}*.wav"))
        if not segments:
            raise ValueError(f"No segments found for preset '{preset_name}' in {segment_dir}")

        logger.info(f"Found {len(segments)} segments for {preset_name}")

        target_samples = target_duration_minutes * 60 * self.sample_rate
        current_samples = 0
        selected = []

        for seg in segments:
            wav, sr = torchaudio.load(str(seg))
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                wav = resampler(wav)
            seg_duration = wav.shape[-1] / self.sample_rate

            if current_samples + wav.shape[-1] > target_samples:
                remaining = target_samples - current_samples
                if remaining > self.sample_rate * 10:
                    selected.append((str(seg), remaining))
                break

            selected.append((str(seg), wav.shape[-1]))
            current_samples += wav.shape[-1]

            if current_samples >= target_samples:
                break

        if not selected:
            raise ValueError("No segments selected")

        logger.info(f"Selected {len(selected)} segments for {target_duration_minutes}min track")

        if output_name is None:
            from datetime import datetime
            output_name = f"hourly_{preset_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.wav"

        result = self.load_audio(selected[0][0])
        if selected[0][1] < result.shape[-1]:
            result = result[..., :selected[0][1]]

        for path, duration in selected[1:]:
            next_audio = self.load_audio(path)
            if duration < next_audio.shape[-1]:
                next_audio = next_audio[..., :duration]
            result = self.crossfade(result, next_audio)

        if result.shape[-1] > target_samples:
            result = result[..., :target_samples]

        output_path = self.output_dir / output_name
        torchaudio.save(str(output_path), result, self.sample_rate)
        actual_duration = result.shape[-1] / self.sample_rate
        logger.info(f"Created hourly track: {output_path} ({actual_duration/60:.1f}min)")
        return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audio Stitcher CLI")
    parser.add_argument("files", nargs="*", help="Audio files to stitch")
    parser.add_argument("--crossfade", type=float, default=2.0, help="Crossfade duration (seconds)")
    parser.add_argument("--sample-rate", type=int, default=32000)
    parser.add_argument("--output", type=str, help="Output filename")
    parser.add_argument("--hourly", action="store_true", help="Create hourly track from directory")
    parser.add_argument("--segment-dir", type=str, help="Directory with segments")
    parser.add_argument("--preset", type=str, help="Preset name for hourly track")
    parser.add_argument("--duration", type=int, default=60, help="Target duration in minutes")
    args = parser.parse_args()

    stitcher = AudioStitcher(
        crossfade_duration=args.crossfade,
        sample_rate=args.sample_rate,
    )

    if args.hourly:
        if not args.segment_dir or not args.preset:
            parser.error("--hourly requires --segment-dir and --preset")
        path = stitcher.create_hourly_track(
            args.segment_dir,
            args.preset,
            target_duration_minutes=args.duration,
        )
        print(f"Created: {path}")
    elif args.files:
        path = stitcher.stitch_files(args.files, output_name=args.output)
        print(f"Created: {path}")
    else:
        parser.error("Provide files to stitch or use --hourly")


if __name__ == "__main__":
    main()