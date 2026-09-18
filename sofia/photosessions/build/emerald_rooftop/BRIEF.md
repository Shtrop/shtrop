# Изумрудный закат на террасе (Emerald Rooftop Sunset)

**ID сессии:** `S05` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 105000

**Референс:** Развитие референса 1 — та же спортивная линия, но терраса на крыше и канонический изумруд персоны

**Настроение:** Спокойная сила и растяжка вместо железа. Изумруд — канон-палитра Sofia, используем его как акцент сессии.

## Гардероб (единый для всех кадров)

`E` — Изумрудный комплект — сигнатурная палитра персоны. Босиком на коврике, обувь только в кадрах у парапета.

```text
deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup
```

## Локация

Закат, открытое небо, город внизу. Свет только естественный, контровой.

```text
private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S05-01 | Наклон вперёд на коврике | hero | 35mm lens | — | 105001 |
| S05-02 | Планка, профиль против неба | core | 50mm lens | — | 105002 |
| S05-03 | Сидит на парапете, город внизу | core | 35mm lens | да | 105003 |
| S05-04 | Растяжка стоя, руки за головой | core | 50mm lens | — | 105004 |
| S05-05 | Поза голубя на коврике | core | 35mm lens | — | 105005 |
| S05-06 | Портрет на закате, изумруд и медь | hero | 85mm portrait lens | — | 105006 |
| S05-07 | Пьёт воду, голова запрокинута | core | 50mm lens | да | 105007 |
| S05-08 | Сидит по-турецки спиной к городу | core | 35mm lens | — | 105008 |
| S05-09 | Деталь: стопы и коврик | filler | 85mm lens | — | 105009 |
| S05-10 | Общий план террасы, силуэт у парапета | core | 24mm wide lens | да | 105010 |

Наушники на шее: 3/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S05-01 — Наклон вперёд на коврике

*hero · seed 105001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, standing forward fold stretch on the yoga mat, legs straight, fingertips reaching the deck, spine long, head turned up toward the camera with direct calm eye contact through the loose strands, 35mm lens, low camera at deck level, three-quarter front angle, full body framing, low golden sun directly behind her rimming the shoulders and calves, warm bounce off the wooden deck onto the face, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-02 — Планка, профиль против неба

*core · seed 105002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, holding a straight-arm plank on the mat, body in one long line, shoulders stacked over wrists, jaw tight, gaze fixed down at the deck, 50mm lens, ground-level camera, strict side profile, full body framing against the open sky, hard contre-jour sunset silhouette with a thin bright rim along the whole body, dark foreground deck, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-03 — Сидит на парапете, город внизу

*core · seed 105003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, white over-ear headphones resting around her neck, sitting sideways on the low concrete parapet with one knee pulled up and the other leg hanging, one hand on the concrete, looking out over the skyline in profile, 35mm lens, eye level, side three-quarter angle, full body framing with the city far below, warm horizontal sunlight across the face and chest, cool blue shadow on the concrete, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-04 — Растяжка стоя, руки за головой

*core · seed 105004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, standing tall on the mat with both hands clasped behind her head, elbows wide, ribcage lifted, torso twisted slightly, eyes closed with the sun on her face, 50mm lens, slightly low angle, frontal, thigh-up framing, direct warm sunset key from camera right, strong modelling on the shoulders and abdomen, olive trees in bokeh behind, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-05 — Поза голубя на коврике

*core · seed 105005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, seated pigeon yoga pose on the mat, one leg folded forward and one extended back, chest open, both hands resting on the front knee, serene expression looking off past the lens, 35mm lens, eye level, side three-quarter angle, full body framing, soft warm side light, long shadow of her body stretching across the deck toward the camera, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-06 — Портрет на закате, изумруд и медь

*hero · seed 105006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, close portrait turned three-quarter to the lens, chin lifted, one hand tucking a loose strand behind the ear, calm confident half-smile with direct eye contact, 85mm portrait lens, eye level, tight head-and-shoulders framing, city bokeh behind, golden hour rim light on the jaw and hair, emerald fabric reading rich against the copper sky, star pendant catching a glint, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-07 — Пьёт воду, голова запрокинута

*core · seed 105007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, white over-ear headphones resting around her neck, standing on the deck drinking from the glass carafe, head tipped back, throat extended, free hand on her hip, eyes closed, 50mm lens, slightly low angle, three-quarter front, waist-up framing, backlit sunset flare through the glass carafe, warm rim along the jawline and arm, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-08 — Сидит по-турецки спиной к городу

*core · seed 105008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, sitting cross-legged in the center of the mat with her back to the skyline, wrists resting on her knees, spine straight in a meditation posture, looking straight into the lens, 35mm lens, eye level, frontal, full body framing, strong backlight from the setting sun behind her head creating a halo through the loose strands, soft reflector fill on the face, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-09 — Деталь: стопы и коврик

*filler · seed 105009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, cropped detail of her bare feet and shins on the sage yoga mat mid-stretch, toes flexed, one hand reaching down into the frame toward the ankle, face out of shot, 85mm lens, close detail framing, shallow depth of field, low warm sun skimming the deck texture, fine grain of the mat and wood visible, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S05-10 — Общий план террасы, силуэт у парапета

*core · seed 105010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green seamless ribbed sports bra with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, fresh dewy skin with no heavy makeup, white over-ear headphones resting around her neck, standing small at the far parapet with a towel over one shoulder, back to the camera, looking out at the city as the sun drops behind the skyline, 24mm wide lens, eye level, wide environmental shot showing the whole terrace, mat and string lights, near-silhouette against a burning orange and violet sky, deck falling into cool shadow, warm flare across the lens, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
