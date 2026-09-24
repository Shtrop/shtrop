#!/usr/bin/env python3
"""Считает длительность клипа LongCat-Video-Avatar 1.5 по константам,
прочитанным из run_demo_avatar_single_audio_to_video.py (без весов и GPU)."""
import re, sys, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                   else "LongCat-Video/run_demo_avatar_single_audio_to_video.py").read_text()

num_frames = int(re.search(r"^\s*num_frames = (\d+)", src, re.M).group(1))
num_cond   = int(re.search(r"^\s*num_cond_frames = (\d+)", src, re.M).group(1))
fps_v15    = int(re.search(r'model_type == "avatar-v1.5":\s*\n\s*save_fps = (\d+)', src).group(1))
fps_v10    = int(re.search(r"^\s*save_fps = (\d+)", src, re.M).group(1))

print(f"num_frames={num_frames}  num_cond_frames={num_cond}  fps(v1.0)={fps_v10}  fps(v1.5)={fps_v15}")
seg0 = num_frames / fps_v15
step = (num_frames - num_cond) / fps_v15
print(f"1-й сегмент = {seg0:.2f} c, каждый следующий +{step:.2f} c\n")

GPU_S_PER_VIDEO_S = 44  # сообщённая цифра для A800-40GB, INT8+distill (не проверено локально)
print(f"{'сегментов':>9} | {'длительность, c':>15} | {'~GPU-время (44x), мин':>22}")
for n in (1, 2, 3, 5, 8, 10, 19):
    d = seg0 + (n - 1) * step
    print(f"{n:>9} | {d:>15.2f} | {d*GPU_S_PER_VIDEO_S/60:>22.1f}")

for target in (15, 30, 60, 90):
    n = 1 + max(0, -(-(target - seg0) // step))
    d = seg0 + (n - 1) * step
    print(f"\nReel {target}s -> нужно {int(n)} сегментов = {d:.2f} c "
          f"(~{d*GPU_S_PER_VIDEO_S/60:.0f} мин GPU при 44x)")
