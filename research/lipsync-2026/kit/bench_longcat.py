#!/usr/bin/env python3
"""Прогон LongCat-Video-Avatar 1.5 с замером пиковой VRAM и времени.

Запускает штатный демо-скрипт через torchrun, параллельно опрашивает nvidia-smi,
считает s_GPU на 1 s видео и пишет report.json с вердиктом по критериям приёмки.

Пример:
    python bench_longcat.py --repo ./LongCat-Video \\
        --checkpoint_dir ./weights/LongCat-Video-Avatar-1.5 \\
        --segments 1 --resolution 480p --vram_budget_gb 24
"""
import argparse, json, os, shutil, subprocess, sys, threading, time

FPS, NUM_FRAMES, NUM_COND_FRAMES = 25, 93, 13   # константы v1.5, см. демо-скрипт


def video_seconds(segments: int) -> float:
    return (NUM_FRAMES + (segments - 1) * (NUM_FRAMES - NUM_COND_FRAMES)) / FPS


def gpu_indices() -> str:
    return os.environ.get("CUDA_VISIBLE_DEVICES", "")


class VramSampler(threading.Thread):
    """Пик memory.used по всем видимым GPU, опрос раз в interval секунд."""

    def __init__(self, interval=1.0):
        super().__init__(daemon=True)
        # ВАЖНО: не называть атрибут _stop — это затирает внутренний Thread._stop(),
        # и join() падает с TypeError: 'Event' object is not callable
        self.interval, self.peak_mib, self.samples = interval, 0, 0
        self._stop_event = threading.Event()
        self.available = shutil.which("nvidia-smi") is not None

    def run(self):
        if not self.available:
            return
        cmd = ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]
        while not self._stop_event.is_set():
            try:
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout
                used = sum(int(v.strip()) for v in out.split("\n") if v.strip())
                self.peak_mib = max(self.peak_mib, used)
                self.samples += 1
            except Exception:
                pass
            self._stop_event.wait(self.interval)

    def stop(self):
        self._stop_event.set()


def torchrun_prefix() -> list:
    """torchrun из PATH, иначе python -m torch.distributed.run (Windows без Scripts в PATH)."""
    exe = shutil.which("torchrun")
    if exe:
        return [exe]
    return [sys.executable, "-m", "torch.distributed.run"]


def build_cmd(a) -> list:
    cmd = torchrun_prefix()
    if a.nproc > 1:
        cmd += [f"--nproc_per_node={a.nproc}"]
    cmd += [
        "run_demo_avatar_single_audio_to_video.py",
        f"--checkpoint_dir={a.checkpoint_dir}",
        f"--stage_1={a.stage_1}",
        f"--input_json={a.input_json}",
        f"--resolution={a.resolution}",
        f"--num_segments={a.segments}",
        "--use_distill", "--model_type", "avatar-v1.5",
        f"--output_dir={a.output_dir}",
    ]
    if a.nproc > 1:
        cmd += [f"--context_parallel_size={a.nproc}"]
    if a.int8:
        cmd += ["--use_int8"]
    if a.vertical:                      # требует patch из longcat-compat.patch
        h, w = (832, 480) if a.resolution == "480p" else (1280, 768)
        cmd += [f"--height={h}", f"--width={w}"]
    return cmd


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default="./LongCat-Video")
    p.add_argument("--checkpoint_dir", default="./weights/LongCat-Video-Avatar-1.5")
    p.add_argument("--input_json", default="assets/avatar/single_example_1.json")
    p.add_argument("--stage_1", default="ai2v", choices=["ai2v", "at2v"])
    p.add_argument("--resolution", default="480p", choices=["480p", "720p"])
    p.add_argument("--segments", type=int, default=1)
    p.add_argument("--nproc", type=int, default=1)
    p.add_argument("--int8", action="store_true", default=True)
    p.add_argument("--no-int8", dest="int8", action="store_false")
    p.add_argument("--vertical", action="store_true", help="9:16 вместо горизонтали")
    p.add_argument("--output_dir", default="./outputs_avatar_single")
    p.add_argument("--vram_budget_gb", type=float, default=24.0)
    p.add_argument("--sec_per_sec_budget", type=float, default=44.0,
                   help="бюджет GPU-секунд на 1 с видео")
    p.add_argument("--report", default="report.json")
    p.add_argument("--dry_run", action="store_true", help="только показать команду и план")
    p.add_argument("--skip_preflight", action="store_true", help="не запускать preflight.py")
    p.add_argument("--no_fix_backend", action="store_true",
                   help="не подгонять attention-бэкенд в конфигах весов")
    p.add_argument("--force", action="store_true", help="запускать даже при FAIL в preflight")
    a = p.parse_args()

    repo = os.path.abspath(a.repo)
    demo = os.path.join(repo, "run_demo_avatar_single_audio_to_video.py")
    if not os.path.isdir(repo):
        print(f"ОШИБКА: каталог репозитория не найден: {repo}\n"
              f"Сначала выполните setup.ps1 / setup.sh — он клонирует LongCat-Video и патчит его.",
              file=sys.stderr)
        return 2
    if not os.path.isfile(demo):
        print(f"ОШИБКА: в {repo} нет run_demo_avatar_single_audio_to_video.py — "
              f"это не клон LongCat-Video.", file=sys.stderr)
        return 2
    ckpt = os.path.abspath(a.checkpoint_dir)
    if not a.dry_run and not os.path.isdir(ckpt):
        print(f"ОШИБКА: каталог весов не найден: {ckpt}\n"
              f"Скачайте их: setup.ps1 -Weights (или setup.sh --weights).", file=sys.stderr)
        return 2

    here = os.path.dirname(os.path.abspath(__file__))
    if not a.dry_run and not a.skip_preflight:
        rc_pf = subprocess.run(
            [sys.executable, os.path.join(here, "preflight.py"),
             "--repo", repo, "--vram_budget_gb", str(a.vram_budget_gb)]).returncode
        if rc_pf != 0 and not a.force:
            print("preflight нашёл блокирующие пункты — исправьте их или запустите с --force",
                  file=sys.stderr)
            return 2
    if not a.dry_run and not a.no_fix_backend:
        subprocess.run([sys.executable, os.path.join(here, "fix_attention_backend.py"), ckpt])

    cmd = build_cmd(a)
    vid_s = video_seconds(a.segments)
    print("repo        :", a.repo)
    print("команда     :", " ".join(cmd))
    print(f"длительность: {vid_s:.2f} c видео ({a.segments} сегм.), GPU: {gpu_indices() or 'все'}")
    if a.dry_run:
        print("dry-run: запуск не выполняется")
        return 0

    env = os.environ.copy()
    if os.name == "nt":
        # torch на Windows собран без libuv, а torchrun по умолчанию просит его:
        # DistStoreError: use_libuv was requested but PyTorch was built without libuv
        env.setdefault("USE_LIBUV", "0")

    sampler = VramSampler()
    sampler.start()
    t0 = time.time()
    try:
        rc = subprocess.run(cmd, cwd=repo, env=env).returncode
    except (FileNotFoundError, NotADirectoryError, OSError) as e:
        sampler.stop()
        print(f"ОШИБКА запуска: {type(e).__name__}: {e}\n"
              f"команда: {' '.join(cmd)}\ncwd: {repo}\n"
              f"Проверьте, что torch установлен в текущем интерпретаторе "
              f"({sys.executable}).", file=sys.stderr)
        return 2
    wall = time.time() - t0
    sampler.stop()
    sampler.join(timeout=5)

    peak_gb = sampler.peak_mib / 1024 if sampler.samples else None
    sec_per_sec = wall / vid_s
    checks = {
        "процесс завершился успешно": rc == 0,
        f"пик VRAM <= {a.vram_budget_gb} GB":
            None if peak_gb is None else peak_gb <= a.vram_budget_gb,
        f"GPU-секунд на 1 с видео <= {a.sec_per_sec_budget}":
            sec_per_sec <= a.sec_per_sec_budget,
    }
    report = {
        "cmd": cmd, "returncode": rc,
        "segments": a.segments, "video_seconds": round(vid_s, 2),
        "wall_seconds": round(wall, 1), "sec_per_video_sec": round(sec_per_sec, 1),
        "peak_vram_gb": None if peak_gb is None else round(peak_gb, 2),
        "vram_samples": sampler.samples,
        "resolution": a.resolution, "vertical": a.vertical, "int8": a.int8, "nproc": a.nproc,
        "checks": checks,
        "verdict": "PASS" if all(v for v in checks.values() if v is not None) else "FAIL",
    }
    if peak_gb is None:
        report["verdict"] = "NOT_MEASURED" if rc == 0 else "FAIL"
        report["note"] = "nvidia-smi недоступен — VRAM не измерена"

    with open(a.report, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n--- результат ---")
    for k, v in checks.items():
        print(f"  {'PASS' if v else 'NOT_MEASURED' if v is None else 'FAIL'}  {k}")
    print(f"  время: {wall:.0f} c на {vid_s:.2f} c видео = {sec_per_sec:.1f} s/s")
    if peak_gb is not None:
        print(f"  пик VRAM: {peak_gb:.2f} GB")
    print(f"вердикт: {report['verdict']}  (отчёт: {a.report})")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
