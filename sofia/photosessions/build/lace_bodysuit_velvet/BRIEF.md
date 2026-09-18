# Кружевное боди в бархате (Lace Bodysuit in Velvet)

**ID сессии:** `S20` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 120000

**Референс:** Серия в кружевном белье — гламурный будуарный регистр

**Настроение:** Бархатный будуар, свечи, шёлковый халат сползает с плеч. Самый тёплый и мягкий сет.

**Подача (слой на каждом кадре):**

```text
lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders
```

## Гардероб (единый для всех кадров)

`T` — Кружевное боди с подкладкой + шёлковый халат, сползающий с плеч.

```text
black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet
```

## Локация

Тёмный бархатный будуар, свечи, тяжёлые ткани, старое зеркало.

```text
dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S20-01 | Халат падает с плеч | hero | 50mm lens | — | 120001 |
| S20-02 | На бархатном диване | hero | 35mm lens | — | 120002 |
| S20-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 120003 |
| S20-04 | Отражение | core | 50mm lens | — | 120004 |
| S20-05 | Силуэт против света | core | 35mm lens | — | 120005 |
| S20-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 120006 |
| S20-07 | Деталь | filler | 85mm lens | — | 120007 |
| S20-08 | Вид сверху | core | 35mm lens | — | 120008 |
| S20-09 | В рост, рука в волосах | core | 50mm lens | — | 120009 |
| S20-10 | Общий план | core | 24mm wide lens | — | 120010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S20-01 — Халат падает с плеч

*hero · seed 120001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, standing in the candlelit room letting the silk robe slide down off both shoulders to her elbows, revealing the lace bodysuit, chin lifted, steady sensual eye contact, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, frontal, thigh-up framing, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candles low and close, warm falloff into the dark velvet behind her, handheld frame tilted a degree or two off level, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-02 — На бархатном диване

*hero · seed 120002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, lying back along the velvet sofa propped on one elbow, robe open and spilling to the floor, one knee raised, the other leg stretched long, languid look down the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at sofa level, three-quarter front angle, full body framing, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, candle key from the floor, deep warm shadows folding into the velvet, slightly underexposed, shadows crushed a little, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-03 — Прогиб, взгляд через плечо

*core · seed 120003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, kneeling back on her heels on the burgundy velvet sofa, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candlelight close and low on her skin, one warm shaft of light through the drapes along her shoulder, one highlight blown out where the light hits hardest, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-04 — Отражение

*core · seed 120004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, standing close to the antique gilt mirror, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candlelight close and low on her skin, one warm shaft of light through the drapes along her shoulder, focus landing a touch behind the eyes, sharpest on the ear, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-05 — Силуэт против света

*core · seed 120005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, standing at the heavily draped window with one shaft of light with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candlelight close and low on her skin, one warm shaft of light through the drapes along her shoulder, faint haze from a smudge on the front element, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-06 — Полулёжа, нога вытянута

*core · seed 120006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, reclining back on the burgundy velvet sofa propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candlelight close and low on her skin, one warm shaft of light through the drapes along her shoulder, slight motion blur in one hand from a slow shutter, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-07 — Деталь

*filler · seed 120007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, cropped detail composition of the lace panel over her ribs and the silk pooling at her elbow, face out of frame, fingers relaxed and naturally posed, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candlelight close and low on her skin, one warm shaft of light through the drapes along her shoulder, subject a little off-centre with one shoulder cropped by the frame edge, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-08 — Вид сверху

*core · seed 120008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, lying on her back on the burgundy velvet sofa, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candlelight close and low on her skin, one warm shaft of light through the drapes along her shoulder, mild flare washing one corner of the frame, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-09 — В рост, рука в волосах

*core · seed 120009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, standing tall among the candles in the middle of the room, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candlelight close and low on her skin, one warm shaft of light through the drapes along her shoulder, grain heavier in the shadows where the exposure was pushed, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S20-10 — Общий план

*core · seed 120010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black lace bodysuit with full opaque lining and delicate lace panels, deep plunging neckline, champagne silk robe worn open and sliding off both shoulders, silver star pendant, hair loose and tousled, bare feet, seen small across the space across the candlelit velvet room, caught mid-movement and not looking at the camera, the room itself carrying the mood, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, sheer-panelled lace bodysuit under a silk robe sliding off both shoulders, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Kodak Portra 800 pushed one stop, candle halation, coarse warm grain, clustered candlelight close and low on her skin, one warm shaft of light through the drapes along her shoulder, colour a touch cool and uncorrected straight out of camera, dark boudoir room, deep burgundy velvet sofa, dozens of lit candles, heavy draped fabrics, antique gilt mirror, low brass table, worn parquet floor, warm shadowed corners, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
