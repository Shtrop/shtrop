# Белое кружево утром (White Lace Morning)

**ID сессии:** `S18` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 118000

**Референс:** Серия в кружевном белье — гламурный будуарный регистр

**Настроение:** Утро, белая постель, мягкий свет через тюль. Нежное белое кружево.

**Подача (слой на каждом кадре):**

```text
lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light
```

## Гардероб (единый для всех кадров)

`R` — Белый кружевной комплект с подкладкой, тонкие бретели, атласный бант.

```text
ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet
```

## Локация

Светлая спальня утром, белое бельё, тюль, пионы.

```text
bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S18-01 | На белой постели, прогиб | hero | 35mm lens | — | 118001 |
| S18-02 | Портрет в утреннем свете | hero | 85mm portrait lens | — | 118002 |
| S18-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 118003 |
| S18-04 | Отражение | core | 50mm lens | — | 118004 |
| S18-05 | Силуэт против света | core | 35mm lens | — | 118005 |
| S18-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 118006 |
| S18-07 | Деталь | filler | 85mm lens | — | 118007 |
| S18-08 | Вид сверху | core | 35mm lens | — | 118008 |
| S18-09 | В рост, рука в волосах | core | 50mm lens | — | 118009 |
| S18-10 | Общий план | core | 24mm wide lens | — | 118010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S18-01 — На белой постели, прогиб

*hero · seed 118001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, kneeling back on her heels in the middle of the white bed in the lace set, spine deeply arched, both hands lifting her hair off her neck, chin down and eyes lifted into the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 35mm lens, slightly above eye level, frontal, full body framing, soft morning sun through sheer curtains wrapping her completely, warm bounce off white linen, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-02 — Портрет в утреннем свете

*hero · seed 118002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, close portrait lying on her side on the pillow, one hand under her cheek, lace strap slipping off the shoulder, lips parted, soft sleepy eye contact, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 85mm portrait lens, low camera at pillow level, head-and-shoulders framing, large soft window key, natural skin texture, warm catchlight in both eyes, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-03 — Прогиб, взгляд через плечо

*core · seed 118003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, kneeling back on her heels on the crisp white linen bed, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, big soft morning sun diffused through the sheer curtain, warm bounce off the white bedding filling every shadow, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-04 — Отражение

*core · seed 118004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, standing close to the leaning floor mirror, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, big soft morning sun diffused through the sheer curtain, warm bounce off the white bedding filling every shadow, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-05 — Силуэт против света

*core · seed 118005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, standing at the tall curtained window with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 35mm lens, eye level, back view, full body vertical framing, big soft morning sun diffused through the sheer curtain, warm bounce off the white bedding filling every shadow, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-06 — Полулёжа, нога вытянута

*core · seed 118006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, reclining back on the crisp white linen bed propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, big soft morning sun diffused through the sheer curtain, warm bounce off the white bedding filling every shadow, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-07 — Деталь

*filler · seed 118007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, cropped detail composition of the satin bow at the centre of the lace and the pendant above it, face out of frame, fingers relaxed and naturally posed, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 85mm lens, close detail framing, very shallow depth of field, big soft morning sun diffused through the sheer curtain, warm bounce off the white bedding filling every shadow, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-08 — Вид сверху

*core · seed 118008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, lying on her back on the crisp white linen bed, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 35mm lens, directly overhead top-down angle, full body framing, big soft morning sun diffused through the sheer curtain, warm bounce off the white bedding filling every shadow, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-09 — В рост, рука в волосах

*core · seed 118009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, standing tall barefoot in the pool of morning sun on the floor, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 50mm lens, slightly low angle, frontal, full body framing, big soft morning sun diffused through the sheer curtain, warm bounce off the white bedding filling every shadow, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S18-10 — Общий план

*core · seed 118010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, ivory white lace lingerie set with full opaque lining, fine floral lace, thin satin straps and a tiny satin bow at the centre, matching lace briefs, silver star pendant, loose soft waves, bare feet, seen small across the space across the bright quiet bedroom, caught mid-movement and not looking at the camera, the room itself carrying the mood, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, white lace glowing in the soft morning light, 24mm wide lens, eye level, wide environmental full-body shot, big soft morning sun diffused through the sheer curtain, warm bounce off the white bedding filling every shadow, bright bedroom in the morning, crisp white linen bed, sheer curtains diffusing the sun, white peonies in a glass vase, pale oak floor, open book on the sheets, dust floating in the light, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
