# Пудровый розовый (Powder Pink)

**ID сессии:** `S29` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 129000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Много света, белая комната, пушистый ковёр. Пудрово-розовый сет с бантами.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin
```

## Гардероб (единый для всех кадров)

`AC` — Пудрово-розовый комплект с подкладкой и атласными бантиками.

```text
powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet
```

## Локация

Светлая пустая комната, огромное окно, глубокий белый ковёр.

```text
bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S29-01 | На пушистом ковре | hero | 35mm lens | — | 129001 |
| S29-02 | Сидя на пятках, спина | hero | 50mm lens | — | 129002 |
| S29-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 129003 |
| S29-04 | Отражение | core | 50mm lens | — | 129004 |
| S29-05 | Против света | core | 35mm lens | — | 129005 |
| S29-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 129006 |
| S29-07 | В рост, рука в волосах | core | 50mm lens | — | 129007 |
| S29-08 | Деталь | filler | 85mm lens | — | 129008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Portra 400, high-key airy grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S29-01 — На пушистом ковре

*hero · seed 129001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet, lying on her front on the deep white rug with ankles crossed in the air and propped on both forearms, back arched, chin on her hands then lifted to the lens with a soft look, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at floor level, frontal, full body framing, shot on Kodak Portra 400, high-key airy grain, broad soft daylight from the big window filling every shadow, handheld frame tilted a degree or two off level, bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S29-02 — Сидя на пятках, спина

*hero · seed 129002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet, kneeling back on her heels on the rug with her back to the camera, both hands lifting her hair off her neck, spine arched, looking over her shoulder into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly above eye level, back view, full body framing, shot on Kodak Portra 400, high-key airy grain, soft window light along her back, gentle warm bounce off the pale rug, slightly underexposed, shadows crushed a little, bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S29-03 — Прогиб, взгляд через плечо

*core · seed 129003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet, kneeling back on her heels on the deep white shag rug, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 400, high-key airy grain, broad soft high-key daylight from the huge window, warm bounce off the pale rug under her, one highlight blown out where the light hits hardest, bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S29-04 — Отражение

*core · seed 129004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet, standing close to the big leaning floor mirror, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Portra 400, high-key airy grain, broad soft high-key daylight from the huge window, warm bounce off the pale rug under her, focus landing a touch behind the eyes, sharpest on the ear, bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S29-05 — Против света

*core · seed 129005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet, standing at the huge curtainless window with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 400, high-key airy grain, broad soft high-key daylight from the huge window, warm bounce off the pale rug under her, faint haze from a smudge on the front element, bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S29-06 — Полулёжа, нога вытянута

*core · seed 129006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet, reclining back on the deep white shag rug propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Portra 400, high-key airy grain, broad soft high-key daylight from the huge window, warm bounce off the pale rug under her, slight motion blur in one hand from a slow shutter, bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S29-07 — В рост, рука в волосах

*core · seed 129007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet, standing tall barefoot in the middle of the bright empty room, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Portra 400, high-key airy grain, broad soft high-key daylight from the huge window, warm bounce off the pale rug under her, subject a little off-centre with one shoulder cropped by the frame edge, bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S29-08 — Деталь

*filler · seed 129008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, powder pink lingerie set with full opaque lining, soft triangle cups with tiny satin bows, matching high-leg briefs with a bow at each hip, silver star pendant, loose soft waves, bare feet, cropped detail composition of the satin bow at her hip and her fingertips resting beside it, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, powder pink set with tiny satin bows, soft high-key light on bare skin, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Portra 400, high-key airy grain, broad soft high-key daylight from the huge window, warm bounce off the pale rug under her, mild flare washing one corner of the frame, bright airy empty room, huge window with no curtains, deep white shag rug, pale plaster walls, one low white chair, a vase of pale roses, blond wood floor, soft overexposed light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
