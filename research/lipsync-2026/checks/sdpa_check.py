#!/usr/bin/env python3
"""Численная проверка SDPA-веток из longcat-compat.patch.

Сверяет выход запасной ветки с эталонным softmax(QK^T*scale)V, посчитанным
вручную. Нужна потому, что в апстриме на месте этой ветки стоял raise, и
проверить её можно только сравнением с определением внимания. GPU не нужен.
"""
import math, sys
import torch

sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else "LongCat-Video")
from longcat_video.modules.attention import Attention, MultiHeadCrossAttention

torch.manual_seed(0)


def reference(q, k, v, scale):
    """softmax(QK^T * scale) V, layout B H S D."""
    w = torch.softmax((q @ k.transpose(-2, -1)) * scale, dim=-1)
    return w @ v


ok = True

# ---------- 1. self-attention ----------
dim, heads, B, S = 64, 4, 2, 7
attn = Attention(dim=dim, num_heads=heads).eval()      # все флаги False -> запасная ветка
D = dim // heads
q, k, v = (torch.randn(B, heads, S, D, dtype=torch.float64) for _ in range(3))
with torch.no_grad():
    got = attn._process_attn(q, k, v, shape=(1, 1, S))
exp = reference(q, k, v, attn.scale)
err = (got - exp).abs().max().item()
print(f"self-attention   : max|Δ| = {err:.2e}  (shape {tuple(got.shape)})")
ok &= err < 1e-10 and got.shape == exp.shape

# ---------- 2. упакованный cross-attention (varlen) ----------
mhca = MultiHeadCrossAttention(dim=dim, num_heads=heads).double().eval()
N, kv_seqlen = 5, [3, 4]
B = len(kv_seqlen)
x = torch.randn(B, N, dim, dtype=torch.float64)
cond = torch.randn(1, sum(kv_seqlen), dim, dtype=torch.float64)
with torch.no_grad():
    out = mhca._process_cross_attn(x, cond, kv_seqlen)

# эталон: то же самое, но по сэмплам, из тех же линейных слоёв
with torch.no_grad():
    q_all = mhca.q_linear(x).view(1, -1, heads, D)
    kv = mhca.kv_linear(cond).view(1, -1, 2, heads, D)
    k_all, v_all = kv.unbind(2)
    q_all, k_all = mhca.q_norm(q_all), mhca.k_norm(k_all)
    outs, off = [], 0
    for i, L in enumerate(kv_seqlen):
        qi = q_all[0, i * N:(i + 1) * N].transpose(0, 1).unsqueeze(0)
        ki = k_all[0, off:off + L].transpose(0, 1).unsqueeze(0)
        vi = v_all[0, off:off + L].transpose(0, 1).unsqueeze(0)
        off += L
        outs.append(reference(qi, ki, vi, 1 / math.sqrt(D)).squeeze(0).transpose(0, 1))
    exp2 = mhca.proj(torch.cat(outs, dim=0).view(B, -1, dim))

err2 = (out - exp2).abs().max().item()
print(f"cross-attn varlen: max|Δ| = {err2:.2e}  (shape {tuple(out.shape)})")
ok &= err2 < 1e-10 and out.shape == (B, N, dim)

print("ИТОГ:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
