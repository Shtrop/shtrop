# Уютная ночь дома (Cozy Night In)

**ID сессии:** `S02` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 102000

**Референс:** Референс 2 — пижама в сердечко, спальня ночью, взгляд через плечо

**Настроение:** Мягкая, домашняя, сонная. Тёплый свет, ночной город за окном, минимум резких теней.

## Гардероб (единый для всех кадров)

`B` — Ткань плотная, непрозрачная. Гольфы и бантики — обязательный continuity-маркер сессии.

```text
cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks
```

## Локация

Одна комната, ночь. Тёплые лампы + холодный город за стеклом — держать этот контраст.

```text
cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S02-01 | Взгляд через плечо на кровати (реконструкция референса) | hero | 35mm lens | — | 102001 |
| S02-02 | На животе перед ноутбуком | core | 50mm lens | да | 102002 |
| S02-03 | Капучино по-турецки на кровати | core | 50mm lens | — | 102003 |
| S02-04 | Силуэт у ночного окна | core | 35mm lens | — | 102004 |
| S02-05 | Отражение в зеркале туалетного столика | core | 50mm lens | — | 102005 |
| S02-06 | Деталь: бантик на гольфе | filler | 85mm macro-leaning lens | — | 102006 |
| S02-07 | Потягивается на краю кровати | core | 35mm lens | — | 102007 |
| S02-08 | Портрет под пледом с мишкой | hero | 85mm portrait lens | — | 102008 |
| S02-09 | Скроллит телефон при свечах, вид сверху | core | 35mm lens | да | 102009 |
| S02-10 | Общий план комнаты из дверного проёма | core | 24mm wide lens | да | 102010 |

Наушники на шее: 3/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S02-01 — Взгляд через плечо на кровати (реконструкция референса)

*hero · seed 102001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, kneeling and sitting back on her heels in the middle of the bed with her back to the camera, spine gently arched, left hand planted on the bedspread beside her, head turned over the right shoulder looking directly into the lens with a soft neutral expression, 35mm lens, slightly above eye level looking down, back three-quarter angle, full body vertical framing, warm vanity lamp and candle glow from camera left, cool blue city window light spilling across her back from the right, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-02 — На животе перед ноутбуком

*core · seed 102002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, white over-ear headphones resting around her neck, lying on her stomach across the bed, ankles crossed and lifted in the air, chin resting on both hands, elbows sinking into the quilt, open laptop in front of her, eyes flicking up to the camera with a small amused smile, 50mm lens, low camera at mattress level, side three-quarter angle, full body framing, cool laptop screen glow on the face, warm fairy lights behind, candle flicker in the background bokeh, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-03 — Капучино по-турецки на кровати

*core · seed 102003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, sitting cross-legged in the center of the bed wrapped loosely in the pink plush blanket, holding a ceramic mug of cappuccino with both hands close to her chest, shoulders relaxed, warm gentle smile toward the lens, 50mm lens, eye level, frontal, waist-up framing, warm candle key from camera right, soft ambient fill, rising steam catching the backlight, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-04 — Силуэт у ночного окна

*core · seed 102004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, standing barefoot-in-socks at the floor-to-ceiling window, one palm and forehead resting against the cold glass, weight on one hip, looking out at the city, seen from behind and slightly to the side, 35mm lens, eye level, back three-quarter angle, full body framing, near-silhouette against the city bokeh, faint warm room light tracing the shoulder and the bun, blue-cyan window color cast, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-05 — Отражение в зеркале туалетного столика

*core · seed 102005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, sitting on the vanity stool leaning in toward the lit mirror, applying lip balm with one finger, other hand steadying on the desk, her face visible in the mirror reflection while the camera sees her from behind, 50mm lens, eye level, over-the-shoulder into the mirror, waist-up framing, even warm bulb light from the mirror frame on the face, dim room behind falling into shadow, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-06 — Деталь: бантик на гольфе

*filler · seed 102006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, cropped detail composition of her knees drawn up on the quilt, one hand adjusting the pink bow on the knit knee-high sock, face out of frame, fingers relaxed and naturally posed, 85mm macro-leaning lens, close detail framing, very shallow depth of field, soft warm side light, candle bokeh balls in the background, gentle texture on the knit and the quilt, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-07 — Потягивается на краю кровати

*core · seed 102007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, sitting on the edge of the bed with feet on the rug, both arms stretched overhead with fingers interlaced, back arched in a sleepy stretch, eyes closed, head tilted back, mid-yawn, 35mm lens, eye level, side three-quarter angle, full body framing, warm bedside lamp key from behind creating a halo through the loose hair, low ambient fill on the front, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-08 — Портрет под пледом с мишкой

*hero · seed 102008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, curled up on her side under the pink plush blanket pulled up to the chin, cream teddy bear tucked beside her cheek, only face and one shoulder visible, big soft eye contact with the camera, 85mm portrait lens, low camera at pillow level, frontal, tight head-and-shoulders framing, single warm candle key close to the face, deep soft shadows, cool city light as a faint hair rim, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-09 — Скроллит телефон при свечах, вид сверху

*core · seed 102009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, white over-ear headphones resting around her neck, lying on her back across the quilt with her head hanging slightly off the edge, holding a phone above her face with both hands, knees bent, one sock-clad foot crossed over the other, absorbed expression, 35mm lens, high three-quarter angle looking down from above the bed, full body framing, cool phone-screen glow on the face and hands, warm candle rim from the side, dark surrounding room, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S02-10 — Общий план комнаты из дверного проёма

*core · seed 102010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, cream white cropped camisole with tiny pink ditsy floral print and thin adjustable straps, matching white ruffled-hem pajama shorts with a small pink heart print and a little satin bow at the waistband, cream knit knee-high socks with pink bows at the cuff, thin silver chain with small star pendant, dark brown messy high bun with loose strands, soft natural makeup with flushed cheeks, white over-ear headphones resting around her neck, seen from across the room sitting small in the middle of the big bed, legs folded, laptop open on her lap, head turned toward the camera as if just noticing it, calm quiet expression, 24mm wide lens, eye level, framed through the bedroom doorway, wide environmental full-body shot, room mostly dark, laptop and fairy lights as the only warm sources, city window glowing cool behind her, cozy modern bedroom at night, floor-to-ceiling window with blurred city bokeh lights, wall of pinned polaroid photographs, vanity desk with a lit mirror and makeup brushes, lit candles, pink tulips in a glass vase, quilted cream bedspread, chunky pink plush throw blanket, cream teddy bear, open laptop glowing, trailing pothos plant, warm string fairy lights, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
