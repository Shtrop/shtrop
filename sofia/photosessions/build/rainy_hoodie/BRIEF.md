# Дождливый день в худи (Rainy Day Hoodie)

**ID сессии:** `S06` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 106000

**Референс:** Развитие референса 3 — та же селфи-эстетика и наушники, но дождь за стеклом вместо неона

**Настроение:** Меланхоличная и уютная. Дождь по стеклу, приглушённый свет, наушники — канон-маркер, здесь используем по максимуму.

## Гардероб (единый для всех кадров)

`F` — Серый меланж на всех кадрах. Молния худи наполовину — под ней всегда белый топ, кадр остаётся SFW.

```text
cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup
```

## Локация

Холодный серый дневной свет + одна тёплая лампа. Дождь на стекле обязателен в кадрах у окна.

```text
quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S06-01 | На подоконнике, наушники, дождь по стеклу | hero | 35mm lens | да | 106001 |
| S06-02 | Рисует пальцем по запотевшему стеклу | core | 50mm lens | да | 106002 |
| S06-03 | Селфи в приглушённом свете | core | 24mm front-facing phone camera look | да | 106003 |
| S06-04 | Ставит пластинку | core | 50mm lens | — | 106004 |
| S06-05 | Портрет у окна, капли на стекле в расфокусе | hero | 85mm portrait lens | — | 106005 |
| S06-06 | Лежит на полу с книгой | core | 35mm lens | да | 106006 |
| S06-07 | Стоит у окна, худи на плече | core | 50mm lens | — | 106007 |
| S06-08 | Деталь: наушники и цепочка | filler | 85mm lens | да | 106008 |
| S06-09 | Танцует одна под пластинку | core | 35mm lens | да | 106009 |
| S06-10 | Общий план комнаты в дождь | core | 24mm wide lens | да | 106010 |

Наушники на шее: 7/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S06-01 — На подоконнике, наушники, дождь по стеклу

*hero · seed 106001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, white over-ear headphones resting around her neck, sitting sideways in the deep window seat with knees pulled up to her chest, white over-ear headphones on, forehead almost touching the rain-streaked glass, head turned toward the camera with a quiet unsmiling gaze, 35mm lens, eye level, three-quarter front angle, full body framing in the window niche, cold grey daylight from the window as the key, single warm lamp glowing from deep in the room, rain shadows dappling her face, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-02 — Рисует пальцем по запотевшему стеклу

*core · seed 106002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, white over-ear headphones resting around her neck, kneeling on the window seat facing the glass, one finger drawing a line through the condensation, other hand flat against the window, seen from behind and slightly to the side, 50mm lens, eye level, back three-quarter angle, waist-up framing, flat cool window light silhouetting her shoulders, faint warm rim from the lamp behind, sharp focus on the droplets, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-03 — Селфи в приглушённом свете

*core · seed 106003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, white over-ear headphones resting around her neck, handheld arm's-length selfie curled up in the window seat under the knitted throw, headphones pushed down around her neck, head resting on the cushion, soft tired smile into the lens, 24mm front-facing phone camera look, slightly above eye level, natural selfie perspective, chest-up framing, soft grey window light on the face, warm lamp accent on the hair, visible low-light grain, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-04 — Ставит пластинку

*core · seed 106004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, crouching in front of the low shelf lowering the needle onto a spinning vinyl record, weight on her toes, one hand steadying on the shelf edge, focused on the turntable, 50mm lens, low camera near floor level, side three-quarter angle, full body framing, warm lamp key from camera left, cool grey window fill from the right, dark room between them, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-05 — Портрет у окна, капли на стекле в расфокусе

*hero · seed 106005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, close portrait pressed close to the window glass, cheek near the surface, eyes lifted to the lens, loose strands sticking to the damp temple, lips slightly parted, 85mm portrait lens, eye level, tight head-and-shoulders framing, out-of-focus raindrops in the foreground, soft cold window key wrapping the face, deep shadow on the far cheek, catchlights shaped like the window, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-06 — Лежит на полу с книгой

*core · seed 106006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, white over-ear headphones resting around her neck, lying on her back on the rug with the knitted throw over her legs, holding an open book above her face, thigh-high socks crossed at the ankles, absorbed in reading, 35mm lens, high top-down angle from above, full body framing, even grey daylight from the window, warm candle pool near her head, soft shadowless falloff, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-07 — Стоит у окна, худи на плече

*core · seed 106007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, standing at the window with arms folded, weight on one hip, hoodie pulled off one shoulder exposing the tank strap, looking out at the rain in profile, 50mm lens, eye level, side profile, thigh-up framing, strong cool window key from the front, dark room behind her, rain streaks projecting across her arm, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-08 — Деталь: наушники и цепочка

*filler · seed 106008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, white over-ear headphones resting around her neck, cropped detail of her collarbones and neck with the white over-ear headphones resting around her neck and the silver star pendant hanging between them, chin cropped at the top of frame, 85mm lens, close detail framing, very shallow depth of field, soft cool side light picking out the skin texture and the brushed metal of the pendant, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-09 — Танцует одна под пластинку

*core · seed 106009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, white over-ear headphones resting around her neck, mid-motion barefoot spin in the middle of the room with headphones on, arms loose above her head, eyes closed, hair strands flying, lost in the music, 35mm lens, slightly low angle, full body framing with mild motion blur in the arms, cool daylight from the window with the warm lamp streaking through the movement, soft ambient shadows, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S06-10 — Общий план комнаты в дождь

*core · seed 106010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cropped heather grey zip hoodie worn half-zipped over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal dewy makeup, white over-ear headphones resting around her neck, seen small from across the room sitting in the window niche with her back against the frame, knees up, mug beside her, dwarfed by the tall grey window, 24mm wide lens, eye level, wide environmental shot showing the whole room and the rain outside, big soft grey window light dominating the frame, warm lamp as a single accent, deep shadow in the foreground, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
