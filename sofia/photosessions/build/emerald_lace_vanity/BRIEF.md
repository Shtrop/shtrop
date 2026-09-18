# Изумрудное кружево и пояс (Emerald Lace and Garters)

**ID сессии:** `S19` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 119000

**Референс:** Серия в кружевном белье — гламурный будуарный регистр

**Настроение:** Винтажный туалетный столик, лампы у зеркала. Изумруд — канон-палитра персоны.

**Подача (слой на каждом кадре):**

```text
lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin
```

## Гардероб (единый для всех кадров)

`S` — Изумрудное кружево с подкладкой, пояс для чулок, чулки. Канон-палитра.

```text
deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet
```

## Локация

Винтажный будуар, туалетный столик с лампами, бархат, латунь.

```text
vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S19-01 | У зеркала, застёгивает чулок | hero | 50mm lens | — | 119001 |
| S19-02 | В отражении, спиной к камере | hero | 35mm lens | — | 119002 |
| S19-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 119003 |
| S19-04 | Отражение | core | 50mm lens | — | 119004 |
| S19-05 | Силуэт против света | core | 35mm lens | — | 119005 |
| S19-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 119006 |
| S19-07 | Деталь | filler | 85mm lens | — | 119007 |
| S19-08 | Вид сверху | core | 35mm lens | — | 119008 |
| S19-09 | В рост, рука в волосах | core | 50mm lens | — | 119009 |
| S19-10 | Общий план | core | 24mm wide lens | — | 119010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S19-01 — У зеркала, застёгивает чулок

*hero · seed 119001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, sitting on the velvet vanity stool with one heel up on the edge, fastening the garter strap to the stocking top, back arched, head turned up to the lens mid-motion, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 50mm lens, eye level, side three-quarter angle, full body framing, warm bulb lights around the mirror throwing even glow on her skin, dim room behind, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-02 — В отражении, спиной к камере

*hero · seed 119002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, standing at the vanity with her back to the camera in the emerald set, one hand on the table, back arched, meeting the lens through her own reflection in the mirror, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 35mm lens, eye level, back view into the mirror, full body framing, mirror bulbs frontal on her face in the reflection, warm rim along her bare back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-03 — Прогиб, взгляд через плечо

*core · seed 119003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, kneeling back on her heels on the velvet chaise beside the vanity, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, warm vanity bulbs wrapping her face and shoulders, a single brass lamp glow along her back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-04 — Отражение

*core · seed 119004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, standing close to the bulb-framed vanity mirror, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, warm vanity bulbs wrapping her face and shoulders, a single brass lamp glow along her back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-05 — Силуэт против света

*core · seed 119005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, standing at the narrow draped window with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 35mm lens, eye level, back view, full body vertical framing, warm vanity bulbs wrapping her face and shoulders, a single brass lamp glow along her back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-06 — Полулёжа, нога вытянута

*core · seed 119006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, reclining back on the velvet chaise beside the vanity propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, warm vanity bulbs wrapping her face and shoulders, a single brass lamp glow along her back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-07 — Деталь

*filler · seed 119007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, cropped detail composition of the garter strap clipped to the stocking top against her thigh, face out of frame, fingers relaxed and naturally posed, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 85mm lens, close detail framing, very shallow depth of field, warm vanity bulbs wrapping her face and shoulders, a single brass lamp glow along her back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-08 — Вид сверху

*core · seed 119008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, lying on her back on the velvet chaise beside the vanity, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 35mm lens, directly overhead top-down angle, full body framing, warm vanity bulbs wrapping her face and shoulders, a single brass lamp glow along her back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-09 — В рост, рука в волосах

*core · seed 119009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, standing tall beside the vanity in the warm bulb light, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 50mm lens, slightly low angle, frontal, full body framing, warm vanity bulbs wrapping her face and shoulders, a single brass lamp glow along her back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S19-10 — Общий план

*core · seed 119010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, deep emerald green lace lingerie set with full opaque lining, matching emerald garter belt with straps, sheer black stockings, silver star pendant, hair pinned up with loose strands, bare feet, seen small across the space across the dim vintage boudoir, caught mid-movement and not looking at the camera, the room itself carrying the mood, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, emerald lace with garter straps and sheer stockings, deep jewel colour against her skin, 24mm wide lens, eye level, wide environmental full-body shot, warm vanity bulbs wrapping her face and shoulders, a single brass lamp glow along her back, vintage boudoir, wooden vanity table with warm bulbs framing the mirror, velvet stool, crystal perfume bottles, brass jewellery tray, patterned wallpaper, heavy drapes, dim warm room, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
