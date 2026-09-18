# Ночной прибой (Night Surf)

**ID сессии:** `S13` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 113000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Луна, прибой, мокрый песок. Промокшая футболка и холодная вода.

**Подача (слой на каждом кадре):**

```text
wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look
```

## Гардероб (единый для всех кадров)

`M` — Огромная мокрая футболка — плотный хлопок, непрозрачная — и низ бикини.

```text
oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot
```

## Локация

Пляж ночью, луна на прибое, пена, отражения на мокром песке.

```text
dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S13-01 | В прибое на коленях | hero | 35mm lens | — | 113001 |
| S13-02 | На мокром песке | hero | 35mm lens | — | 113002 |
| S13-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 113003 |
| S13-04 | Отражение | core | 50mm lens | — | 113004 |
| S13-05 | Силуэт против света | core | 35mm lens | — | 113005 |
| S13-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 113006 |
| S13-07 | Деталь | filler | 85mm lens | — | 113007 |
| S13-08 | Вид сверху | core | 35mm lens | — | 113008 |
| S13-09 | В рост, рука в волосах | core | 50mm lens | — | 113009 |
| S13-10 | Общий план | core | 24mm wide lens | — | 113010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S13-01 — В прибое на коленях

*hero · seed 113001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, kneeling in the shallow surf as a wave breaks around her thighs, soaked tee clinging, both hands wringing the water out of her hair, chin lifted, looking up into the lens, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at water level, frontal, full body framing, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind rimming the wet fabric and hair, foam glowing white, handheld frame tilted a degree or two off level, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-02 — На мокром песке

*hero · seed 113002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, lying back on the wet sand with foam running around her, one knee raised, both arms thrown above her head, wet tee and hair full of sand, eyes on the lens, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, high three-quarter angle from above, full body framing, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, moonlight straight down on her, mirror reflections in the wet sand around her, slightly underexposed, shadows crushed a little, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-03 — Прогиб, взгляд через плечо

*core · seed 113003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, kneeling back on her heels on the cold wet sand, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind her, rimming the wet fabric, warm distant pier lights glinting in the water, one highlight blown out where the light hits hardest, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-04 — Отражение

*core · seed 113004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, standing close to the sheet of water on the wet sand, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind her, rimming the wet fabric, warm distant pier lights glinting in the water, focus landing a touch behind the eyes, sharpest on the ear, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-05 — Силуэт против света

*core · seed 113005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, standing at the breaking surf line with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind her, rimming the wet fabric, warm distant pier lights glinting in the water, faint haze from a smudge on the front element, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-06 — Полулёжа, нога вытянута

*core · seed 113006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, reclining back on the cold wet sand propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind her, rimming the wet fabric, warm distant pier lights glinting in the water, slight motion blur in one hand from a slow shutter, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-07 — Деталь

*filler · seed 113007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, cropped detail composition of wet sand clinging to her shin and the dripping hem of the tee, face out of frame, fingers relaxed and naturally posed, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind her, rimming the wet fabric, warm distant pier lights glinting in the water, subject a little off-centre with one shoulder cropped by the frame edge, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-08 — Вид сверху

*core · seed 113008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, lying on her back on the cold wet sand, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind her, rimming the wet fabric, warm distant pier lights glinting in the water, mild flare washing one corner of the frame, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-09 — В рост, рука в волосах

*core · seed 113009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, standing tall ankle-deep in the running surf, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind her, rimming the wet fabric, warm distant pier lights glinting in the water, grain heavier in the shadows where the exposure was pushed, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S13-10 — Общий план

*core · seed 113010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized soaked white cotton t-shirt, heavy opaque cotton clinging to her body, black bikini bottoms underneath, wet sandy legs, dripping wet hair, silver star pendant, barefoot, seen small across the space far down the empty moonlit beach, caught mid-movement and not looking at the camera, the room itself carrying the mood, wet-tee glamour, heavy soaked cotton clinging to her shape, long bare wet legs, sand on her skin, wild hair and a challenging look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Cinestill 800T pushed one stop, coarse grain, moonlight halation, hard cold moonlight from behind her, rimming the wet fabric, warm distant pier lights glinting in the water, colour a touch cool and uncorrected straight out of camera, dark empty beach at night, moonlight silvering the surf, foam running up the sand, mirror reflections on the wet sand, distant pier lights on the horizon, cool blue darkness, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
