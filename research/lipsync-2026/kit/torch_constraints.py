#!/usr/bin/env python3
"""Печатает pip-constraints, фиксирующие уже установленные torch-пакеты.

Нужен, чтобы установка requirements не подменила рабочую CUDA-сборку колесом
с PyPI (под Windows они собраны без CUDA). Вывод — в файл, который передаётся
в pip через -c.

    python torch_constraints.py > constraints-torch.txt
"""
import importlib.metadata as md
import sys

PACKAGES = ("torch", "torchvision", "torchaudio")

found = 0
for name in PACKAGES:
    try:
        version = md.version(name)
    except md.PackageNotFoundError:
        continue
    print(f"{name}=={version}")
    found += 1

if not found:
    print("# ни один из torch-пакетов не установлен", file=sys.stderr)
