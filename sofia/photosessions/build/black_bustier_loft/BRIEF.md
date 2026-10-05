# Чёрный бюстье в лофте (Black Bustier Loft)

**ID сессии:** `S23` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 123000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Бетон, жёсткий свет из высоких окон, чёрный бюстье на косточках. Графично и дерзко.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete
```

## Гардероб (единый для всех кадров)

`W` — Чёрный бюстье на косточках + высокие трусики, плотная ткань, чулки.

```text
black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet
```

## Локация

Пустой бетонный лофт, высокие окна, минимум мебели.

```text
empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S23-01 | У бетонной колонны | hero | 35mm lens | — | 123001 |
| S23-02 | Сидя на полу, нога вытянута | hero | 35mm lens | — | 123002 |
| S23-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 123003 |
| S23-04 | Отражение | core | 50mm lens | — | 123004 |
| S23-05 | Против света | core | 35mm lens | — | 123005 |
| S23-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 123006 |
| S23-07 | В рост, рука в волосах | core | 50mm lens | — | 123007 |
| S23-08 | Деталь | filler | 85mm lens | — | 123008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Ektar 100, tight grain and deep blacks
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S23-01 — У бетонной колонны

*hero · seed 123001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet, standing with her back against the concrete column in the black bustier and high-waisted briefs, one heel propped behind her, both hands behind her lower back, chest lifted, level stare at the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly low angle, frontal, full body framing, shot on Kodak Ektar 100, tight grain and deep blacks, hard shaft of daylight from the high loft window cutting across her torso, handheld frame tilted a degree or two off level, empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S23-02 — Сидя на полу, нога вытянута

*hero · seed 123002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet, sitting on the bare concrete floor with one leg stretched long and the other bent up, leaning back on both hands, shoulders open, head tipped back then turned to hold the camera, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at floor level, three-quarter front angle, full body framing, shot on Kodak Ektar 100, tight grain and deep blacks, raking window light along the floor and her legs, hard shadow shapes on the concrete, slightly underexposed, shadows crushed a little, empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S23-03 — Прогиб, взгляд через плечо

*core · seed 123003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet, kneeling back on her heels on the bare concrete floor, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Ektar 100, tight grain and deep blacks, hard directional daylight from the tall window, cold bounce off the pale concrete wall behind her, one highlight blown out where the light hits hardest, empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S23-04 — Отражение

*core · seed 123004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet, standing close to the leaning sheet of glass against the wall, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Ektar 100, tight grain and deep blacks, hard directional daylight from the tall window, cold bounce off the pale concrete wall behind her, focus landing a touch behind the eyes, sharpest on the ear, empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S23-05 — Против света

*core · seed 123005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet, standing at the tall steel-framed loft window with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Kodak Ektar 100, tight grain and deep blacks, hard directional daylight from the tall window, cold bounce off the pale concrete wall behind her, faint haze from a smudge on the front element, empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S23-06 — Полулёжа, нога вытянута

*core · seed 123006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet, reclining back on the bare concrete floor propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Ektar 100, tight grain and deep blacks, hard directional daylight from the tall window, cold bounce off the pale concrete wall behind her, slight motion blur in one hand from a slow shutter, empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S23-07 — В рост, рука в волосах

*core · seed 123007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet, standing tall in the middle of the empty concrete floor, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Ektar 100, tight grain and deep blacks, hard directional daylight from the tall window, cold bounce off the pale concrete wall behind her, subject a little off-centre with one shoulder cropped by the frame edge, empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S23-08 — Деталь

*filler · seed 123008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black boned bustier with structured cups and visible seams, opaque matte fabric, matching high-waisted black briefs, sheer black stockings, silver star pendant, hair in a sleek low bun with loose strands, bare feet, cropped detail composition of the boning seams of the bustier across her ribs and her hand resting there, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, boned bustier pulling the waist in hard, graphic black against raw concrete, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Ektar 100, tight grain and deep blacks, hard directional daylight from the tall window, cold bounce off the pale concrete wall behind her, mild flare washing one corner of the frame, empty industrial loft, raw concrete floor and columns, tall steel-framed windows, peeling white paint, a single wooden stool, dust in the light shafts, cold daylight, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
