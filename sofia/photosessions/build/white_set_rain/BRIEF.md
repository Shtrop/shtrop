# Белый комплект и дождь (White Set in the Rain)

**ID сессии:** `S26` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 126000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Серый дождливый свет, белое бельё, его рубашка на плечах. Холодно и нежно.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders
```

## Гардероб (единый для всех кадров)

`Z` — Белый бельевой комплект с подкладкой + огромная белая рубашка с плеч.

```text
crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet
```

## Локация

Тихая квартира в дождь, глубокий подоконник, капли по стеклу.

```text
quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S26-01 | Рубашка падает с плеч у окна | hero | 35mm lens | — | 126001 |
| S26-02 | На подоконнике, колени подняты | hero | 50mm lens | — | 126002 |
| S26-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 126003 |
| S26-04 | Отражение | core | 50mm lens | — | 126004 |
| S26-05 | Против света | core | 35mm lens | — | 126005 |
| S26-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 126006 |
| S26-07 | В рост, рука в волосах | core | 50mm lens | — | 126007 |
| S26-08 | Деталь | filler | 85mm lens | — | 126008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Fujifilm Pro 400H, cool muted grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S26-01 — Рубашка падает с плеч у окна

*hero · seed 126001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet, standing at the rain-streaked window letting the oversized white shirt slide off both shoulders to her elbows over the white set, back arched, head turned to the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, three-quarter front angle, full body framing, shot on Fujifilm Pro 400H, cool muted grain, flat cold daylight through the wet glass, rain shadows moving across her skin, handheld frame tilted a degree or two off level, quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S26-02 — На подоконнике, колени подняты

*hero · seed 126002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet, sitting up on the deep windowsill with both knees drawn up and apart, shirt open, one hand on the cold glass beside her, level unsmiling gaze into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, frontal, full body framing, shot on Fujifilm Pro 400H, cool muted grain, cool window light as the only key, dark room swallowing everything behind her, slightly underexposed, shadows crushed a little, quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S26-03 — Прогиб, взгляд через плечо

*core · seed 126003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet, kneeling back on her heels on the deep linen-cushioned windowsill, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Fujifilm Pro 400H, cool muted grain, broad cold daylight through the rain-streaked glass, faint warm spill from the hallway behind her, one highlight blown out where the light hits hardest, quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S26-04 — Отражение

*core · seed 126004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet, standing close to the dark window glass itself, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Fujifilm Pro 400H, cool muted grain, broad cold daylight through the rain-streaked glass, faint warm spill from the hallway behind her, focus landing a touch behind the eyes, sharpest on the ear, quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S26-05 — Против света

*core · seed 126005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet, standing at the tall rain-streaked window with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Fujifilm Pro 400H, cool muted grain, broad cold daylight through the rain-streaked glass, faint warm spill from the hallway behind her, faint haze from a smudge on the front element, quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S26-06 — Полулёжа, нога вытянута

*core · seed 126006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet, reclining back on the deep linen-cushioned windowsill propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Fujifilm Pro 400H, cool muted grain, broad cold daylight through the rain-streaked glass, faint warm spill from the hallway behind her, slight motion blur in one hand from a slow shutter, quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S26-07 — В рост, рука в волосах

*core · seed 126007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet, standing tall in the middle of the dim room facing the window, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Fujifilm Pro 400H, cool muted grain, broad cold daylight through the rain-streaked glass, faint warm spill from the hallway behind her, subject a little off-centre with one shoulder cropped by the frame edge, quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S26-08 — Деталь

*filler · seed 126008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, crisp white lingerie set with full opaque lining, plain smooth cups and high-cut briefs, oversized white men's shirt worn open and hanging off both shoulders, silver star pendant, damp loose hair, bare feet, cropped detail composition of raindrops on the glass in front of her shoulder and the open shirt cuff at her wrist, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, crisp white set under an oversized shirt hanging off both shoulders, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Fujifilm Pro 400H, cool muted grain, broad cold daylight through the rain-streaked glass, faint warm spill from the hallway behind her, mild flare washing one corner of the frame, quiet apartment on a rainy afternoon, tall window covered in rain streaks, deep windowsill with a linen cushion, grey city blurred beyond, pale walls, dark wood floor, one unlit lamp, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
