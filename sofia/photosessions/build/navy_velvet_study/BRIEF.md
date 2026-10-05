# Синий бархат в кабинете (Navy Velvet Study)

**ID сессии:** `S27` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 127000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Старый кабинет, книги до потолка, настольная лампа. Тёмно-синий бархатный сет.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books
```

## Гардероб (единый для всех кадров)

`AA` — Тёмно-синий бархатный комплект с подкладкой, глубокий вырез.

```text
deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet
```

## Локация

Кабинет со стеллажами до потолка, кожаное кресло, зелёная лампа.

```text
old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S27-01 | На письменном столе | hero | 35mm lens | — | 127001 |
| S27-02 | В кожаном кресле, спиной | hero | 50mm lens | — | 127002 |
| S27-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 127003 |
| S27-04 | Отражение | core | 50mm lens | — | 127004 |
| S27-05 | Против света | core | 35mm lens | — | 127005 |
| S27-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 127006 |
| S27-07 | В рост, рука в волосах | core | 50mm lens | — | 127007 |
| S27-08 | Деталь | filler | 85mm lens | — | 127008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Portra 800, warm lamp halation and grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S27-01 — На письменном столе

*hero · seed 127001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet, sitting up on the edge of the heavy desk in the navy velvet set, one leg stretched to the floor and the other bent up on the wood, leaning back on one hand, chin raised, level gaze at the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly low angle, three-quarter front, full body framing, shot on Kodak Portra 800, warm lamp halation and grain, warm desk lamp close from the side, deep shadow across the bookshelves behind, handheld frame tilted a degree or two off level, old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S27-02 — В кожаном кресле, спиной

*hero · seed 127002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet, kneeling up in the worn leather armchair with her back to the camera, both hands on the chair back, spine deeply arched, looking over her shoulder into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, back three-quarter angle, full body framing, shot on Kodak Portra 800, warm lamp halation and grain, single lamp raking along her back, warm falloff into the dark study, slightly underexposed, shadows crushed a little, old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S27-03 — Прогиб, взгляд через плечо

*core · seed 127003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet, kneeling back on her heels on the heavy oak desk, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 800, warm lamp halation and grain, one warm desk lamp close and low on her, faint cool light from the curtained window behind, one highlight blown out where the light hits hardest, old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S27-04 — Отражение

*core · seed 127004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet, standing close to the dark glass of the bookcase door, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Portra 800, warm lamp halation and grain, one warm desk lamp close and low on her, faint cool light from the curtained window behind, focus landing a touch behind the eyes, sharpest on the ear, old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S27-05 — Против света

*core · seed 127005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet, standing at the narrow curtained study window with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 800, warm lamp halation and grain, one warm desk lamp close and low on her, faint cool light from the curtained window behind, faint haze from a smudge on the front element, old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S27-06 — Полулёжа, нога вытянута

*core · seed 127006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet, reclining back on the heavy oak desk propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Portra 800, warm lamp halation and grain, one warm desk lamp close and low on her, faint cool light from the curtained window behind, slight motion blur in one hand from a slow shutter, old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S27-07 — В рост, рука в волосах

*core · seed 127007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet, standing tall in the pool of lamplight between the shelves, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Portra 800, warm lamp halation and grain, one warm desk lamp close and low on her, faint cool light from the curtained window behind, subject a little off-centre with one shoulder cropped by the frame edge, old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S27-08 — Деталь

*filler · seed 127008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, deep navy velvet lingerie set with full opaque lining, plunging balconette cut and high-leg briefs, sheer navy stockings, silver star pendant, hair pinned up loosely, bare feet, cropped detail composition of the velvet edge of the cup and the pendant lying against her skin, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, deep navy velvet set with a plunging neckline against old leather and books, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Portra 800, warm lamp halation and grain, one warm desk lamp close and low on her, faint cool light from the curtained window behind, mild flare washing one corner of the frame, old private study, floor-to-ceiling bookshelves, heavy oak desk, worn leather armchair, green glass desk lamp, globe, persian rug, dark panelled walls, warm pooled light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
