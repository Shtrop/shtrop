# Шёлк на террасе ночью (Silk on the Terrace)

**ID сессии:** `S24` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 124000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Тёплая ночь, город внизу, короткая шёлковая двойка. Ветер и свечи.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze
```

## Гардероб (единый для всех кадров)

`X` — Короткая шёлковая двойка: топ на тонких бретелях и очень короткие шорты.

```text
short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet
```

## Локация

Терраса на крыше тёплой ночью, свечи, город внизу.

```text
rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S24-01 | У парапета, ветер в шёлке | hero | 35mm lens | — | 124001 |
| S24-02 | В плетёном кресле | hero | 50mm lens | — | 124002 |
| S24-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 124003 |
| S24-04 | Отражение | core | 50mm lens | — | 124004 |
| S24-05 | Против света | core | 35mm lens | — | 124005 |
| S24-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 124006 |
| S24-07 | В рост, рука в волосах | core | 50mm lens | — | 124007 |
| S24-08 | Деталь | filler | 85mm lens | — | 124008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T, halation around the city lights
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S24-01 — У парапета, ветер в шёлке

*hero · seed 124001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet, standing at the terrace parapet in the short silk set with the breeze lifting the hem, both hands on the stone behind her, back arched, head turned over her shoulder to the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back three-quarter angle, full body framing, shot on Cinestill 800T, halation around the city lights, warm candle clusters on the parapet from below, cool city glow behind her, handheld frame tilted a degree or two off level, rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S24-02 — В плетёном кресле

*hero · seed 124002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet, sitting sideways in the low rattan chair with both legs draped over one arm of it, silk shorts riding high, one hand holding a glass, slow amused look down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, three-quarter front angle, full body framing, shot on Cinestill 800T, halation around the city lights, candlelight close and warm on her skin, deep blue night beyond the terrace, slightly underexposed, shadows crushed a little, rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S24-03 — Прогиб, взгляд через плечо

*core · seed 124003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet, kneeling back on her heels on the wide stone parapet ledge, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, halation around the city lights, warm candlelight low and close on her skin, cool city glow drawing her whole outline, one highlight blown out where the light hits hardest, rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S24-04 — Отражение

*core · seed 124004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet, standing close to the dark glass of the terrace door, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T, halation around the city lights, warm candlelight low and close on her skin, cool city glow drawing her whole outline, focus landing a touch behind the eyes, sharpest on the ear, rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S24-05 — Против света

*core · seed 124005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet, standing at the open edge of the terrace above the city with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, halation around the city lights, warm candlelight low and close on her skin, cool city glow drawing her whole outline, faint haze from a smudge on the front element, rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S24-06 — Полулёжа, нога вытянута

*core · seed 124006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet, reclining back on the wide stone parapet ledge propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T, halation around the city lights, warm candlelight low and close on her skin, cool city glow drawing her whole outline, slight motion blur in one hand from a slow shutter, rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S24-07 — В рост, рука в волосах

*core · seed 124007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet, standing tall at the edge of the terrace with the city behind her, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, halation around the city lights, warm candlelight low and close on her skin, cool city glow drawing her whole outline, subject a little off-centre with one shoulder cropped by the frame edge, rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S24-08 — Деталь

*filler · seed 124008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short ink-blue silk set, thin-strap cami with lace edging and very short matching silk shorts, heavy opaque silk, silver star pendant, hair loose and moving in the breeze, bare feet, cropped detail composition of the silk hem lifting off her thigh in the breeze, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, short silk cami and shorts lifting in the night breeze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T, halation around the city lights, warm candlelight low and close on her skin, cool city glow drawing her whole outline, mild flare washing one corner of the frame, rooftop terrace on a warm night, low stone parapet, clusters of lit candles, rattan lounge chair, olive tree in a pot, string lights unlit, city lights spread out far below, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
