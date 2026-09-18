# Сатиновая комбинация (Champagne Satin)

**ID сессии:** `S22` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 122000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Отель утром, тяжёлый сатин цвета шампань, свет из-за шторы. Медленно и дорого.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips
```

## Гардероб (единый для всех кадров)

`V` — Короткая сатиновая комбинация цвета шампань на тонких бретелях, плотная подкладка.

```text
short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet
```

## Локация

Отельный номер утром, смятая постель, тяжёлая шторa приоткрыта.

```text
hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S22-01 | Бретель сползает с плеча | hero | 50mm lens | — | 122001 |
| S22-02 | На животе, взгляд назад | hero | 35mm lens | — | 122002 |
| S22-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 122003 |
| S22-04 | Отражение | core | 50mm lens | — | 122004 |
| S22-05 | Против света | core | 35mm lens | — | 122005 |
| S22-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 122006 |
| S22-07 | В рост, рука в волосах | core | 50mm lens | — | 122007 |
| S22-08 | Деталь | filler | 85mm lens | — | 122008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Portra 800, warm grain in the shadow side
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S22-01 — Бретель сползает с плеча

*hero · seed 122001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet, standing beside the unmade bed in the short satin slip, one hand lifting her hair off her neck while the other strap slides down her arm, back arched, chin lowered, eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, frontal, thigh-up framing, shot on Kodak Portra 800, warm grain in the shadow side, one soft blade of morning light from the curtain gap across her chest and face, handheld frame tilted a degree or two off level, hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S22-02 — На животе, взгляд назад

*hero · seed 122002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet, lying on her stomach across the bed with ankles crossed in the air, propped on both forearms so the satin rides high on her thighs, back deeply arched, looking back over her shoulder, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at bed level, back three-quarter angle, full body framing, shot on Kodak Portra 800, warm grain in the shadow side, warm side light raking along the satin, deep folds of shadow in the sheets, slightly underexposed, shadows crushed a little, hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S22-03 — Прогиб, взгляд через плечо

*core · seed 122003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet, kneeling back on her heels on the unmade hotel bed, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 800, warm grain in the shadow side, a single warm blade of morning light through the curtain gap, soft bounce off the white linen filling the shadows, one highlight blown out where the light hits hardest, hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S22-04 — Отражение

*core · seed 122004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet, standing close to the tall mirror by the wardrobe, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Portra 800, warm grain in the shadow side, a single warm blade of morning light through the curtain gap, soft bounce off the white linen filling the shadows, focus landing a touch behind the eyes, sharpest on the ear, hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S22-05 — Против света

*core · seed 122005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet, standing at the gap in the heavy hotel curtain with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 800, warm grain in the shadow side, a single warm blade of morning light through the curtain gap, soft bounce off the white linen filling the shadows, faint haze from a smudge on the front element, hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S22-06 — Полулёжа, нога вытянута

*core · seed 122006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet, reclining back on the unmade hotel bed propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Portra 800, warm grain in the shadow side, a single warm blade of morning light through the curtain gap, soft bounce off the white linen filling the shadows, slight motion blur in one hand from a slow shutter, hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S22-07 — В рост, рука в волосах

*core · seed 122007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet, standing tall in the middle of the hotel room floor, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Portra 800, warm grain in the shadow side, a single warm blade of morning light through the curtain gap, soft bounce off the white linen filling the shadows, subject a little off-centre with one shoulder cropped by the frame edge, hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S22-08 — Деталь

*filler · seed 122008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short champagne satin slip with thin adjustable straps and a lace trim hem, heavy opaque satin with a liquid sheen, matching satin briefs, silver star pendant, loose bed hair, bare feet, cropped detail composition of the satin strap fallen to her upper arm and the pendant on her collarbone, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid satin catching the morning light as it slips, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Portra 800, warm grain in the shadow side, a single warm blade of morning light through the curtain gap, soft bounce off the white linen filling the shadows, mild flare washing one corner of the frame, hotel room in the morning, unmade bed with heavy white linen, thick curtain open a hand's width, dark wood furniture, brass lamp, coffee tray, city haze outside, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
