# Шёлковая простыня (Champagne Silk)

**ID сессии:** `S14` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 114000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Отель, раннее утро, тяжёлый шёлк. Открытая спина, закрытый кадр.

**Подача (слой на каждом кадре):**

```text
covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder
```

## Гардероб (единый для всех кадров)

`N` — Открытая спина, шёлк держится спереди рукой — ничего не обнажено.

```text
champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair
```

## Локация

Отельная кровать ранним утром, тяжёлые шторы приоткрыты.

```text
hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S14-01 | Открытая спина у окна | hero | 50mm lens | — | 114001 |
| S14-02 | На животе, взгляд через плечо | hero | 35mm lens | — | 114002 |
| S14-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 114003 |
| S14-04 | Отражение | core | 50mm lens | — | 114004 |
| S14-05 | Силуэт против света | core | 35mm lens | — | 114005 |
| S14-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 114006 |
| S14-07 | Деталь | filler | 85mm lens | — | 114007 |
| S14-08 | Вид сверху | core | 35mm lens | — | 114008 |
| S14-09 | В рост, рука в волосах | core | 50mm lens | — | 114009 |
| S14-10 | Общий план | core | 24mm wide lens | — | 114010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S14-01 — Открытая спина у окна

*hero · seed 114001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, standing at the gap in the heavy curtains with the silk gathered and held at her front, entire bare back to the camera, weight on one hip, head turned in profile into the light, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 50mm lens, eye level, back view, full body vertical framing, one cool blade of morning light down her spine, warm lamp glow on the far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-02 — На животе, взгляд через плечо

*hero · seed 114002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, lying on her stomach across the silk, propped on both forearms with the sheet drawn across her front, bare back and shoulders, ankles crossed in the air, looking back over her shoulder, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 35mm lens, low camera at bed level, back three-quarter angle, full body framing, soft directional morning light along the curve of her back, deep shadow in the folds of silk, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-03 — Прогиб, взгляд через плечо

*core · seed 114003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, kneeling back on her heels on the champagne silk of the bed, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, a single blade of cool morning light through the curtain gap, warm brass lamp glow on her far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-04 — Отражение

*core · seed 114004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, standing close to the dark hotel mirror across the room, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, a single blade of cool morning light through the curtain gap, warm brass lamp glow on her far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-05 — Силуэт против света

*core · seed 114005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, standing at the gap in the heavy curtains with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 35mm lens, eye level, back view, full body vertical framing, a single blade of cool morning light through the curtain gap, warm brass lamp glow on her far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-06 — Полулёжа, нога вытянута

*core · seed 114006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, reclining back on the champagne silk of the bed propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, a single blade of cool morning light through the curtain gap, warm brass lamp glow on her far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-07 — Деталь

*filler · seed 114007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, cropped detail composition of the silk gathered in her fist and the line of her bare shoulder blade, face out of frame, fingers relaxed and naturally posed, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 85mm lens, close detail framing, very shallow depth of field, a single blade of cool morning light through the curtain gap, warm brass lamp glow on her far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-08 — Вид сверху

*core · seed 114008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, lying on her back on the champagne silk of the bed, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 35mm lens, directly overhead top-down angle, full body framing, a single blade of cool morning light through the curtain gap, warm brass lamp glow on her far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-09 — В рост, рука в волосах

*core · seed 114009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, standing tall beside the bed with the sheet trailing behind her, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 50mm lens, slightly low angle, frontal, full body framing, a single blade of cool morning light through the curtain gap, warm brass lamp glow on her far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S14-10 — Общий план

*core · seed 114010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, champagne silk sheet drawn across her front and held in place with one hand, bare back and shoulders, nothing exposed, silver star pendant, loose bed hair, seen small across the space on the far side of the big hotel bed, caught mid-movement and not looking at the camera, the room itself carrying the mood, covered-front editorial glamour, bare back and shoulders with the heavy silk held across her front so nothing is exposed, long unbroken line of the spine, soft morning gaze back over the shoulder, 24mm wide lens, eye level, wide environmental full-body shot, a single blade of cool morning light through the curtain gap, warm brass lamp glow on her far shoulder, hotel bed in the early morning, heavy champagne silk sheets, thick curtains half drawn, a blade of city light across the bed, dark wood headboard, brass lamp, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
