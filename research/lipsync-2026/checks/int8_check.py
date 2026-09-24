#!/usr/bin/env python3
"""CPU-проверка модуля INT8-квантизации из LongCat-Video (--use_int8).
Без весов модели: берём реальный код репозитория и меряем ошибку/экономию памяти."""
import sys, torch, torch.nn as nn
sys.path.insert(0, "LongCat-Video")
from longcat_video.modules.quantization import QuantizedLinear, quantize_model, DEFAULT_SKIP_PATTERNS

torch.manual_seed(0)

class Block(nn.Module):
    def __init__(self, d=3072, mlp=4):
        super().__init__()
        self.qkv = nn.Linear(d, 3*d, bias=True)
        self.proj = nn.Linear(d, d, bias=True)
        self.fc1 = nn.Linear(d, mlp*d, bias=True)
        self.fc2 = nn.Linear(mlp*d, d, bias=True)
    def forward(self, x):
        return self.fc2(torch.nn.functional.gelu(self.fc1(self.proj(self.qkv(x)[..., :x.shape[-1]]))))

def nbytes(m):
    return sum(p.numel()*p.element_size() for p in m.parameters()) + \
           sum(b.numel()*b.element_size() for b in m.buffers())

m = Block().to(torch.bfloat16).eval()
x = torch.randn(2, 128, 3072, dtype=torch.bfloat16)
with torch.no_grad():
    ref = m(x).float()

before = nbytes(m)
q = quantize_model(m)
after = nbytes(q)
n_q = sum(1 for _ in [mm for mm in q.modules() if isinstance(mm, QuantizedLinear)])

with torch.no_grad():
    out = q(x).float()

rel = ((out - ref).norm() / ref.norm()).item()
cos = torch.nn.functional.cosine_similarity(out.flatten(), ref.flatten(), dim=0).item()
print(f"квантовано слоёв Linear -> QuantizedLinear : {n_q}")
print(f"skip-паттерны по умолчанию               : {sorted(DEFAULT_SKIP_PATTERNS)}")
print(f"память весов блока  bf16 -> int8         : {before/2**20:.1f} MiB -> {after/2**20:.1f} MiB "
      f"({before/after:.2f}x меньше)")
print(f"относительная ошибка выхода ||dy||/||y|| : {rel:.4f}")
print(f"косинусная близость к bf16-выходу        : {cos:.6f}")
print("схема: per-channel symmetric weight-only; в forward вес деквантизуется "
      "в dtype активаций -> экономия VRAM есть, ускорения матмулов нет")
