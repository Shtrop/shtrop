# Серебро и дым (Silver and Smoke)

**ID сессии:** `S31` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 131000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Ночная студия, дым, жёсткий импульс. Серебристый металлик-сет. Самый графичный набор.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke
```

## Гардероб (единый для всех кадров)

`AE` — Серебристый металлик-комплект с подкладкой, гладкая ткань.

```text
liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet
```

## Локация

Тёмная студия с дымом, один жёсткий импульсный источник, чёрный куб.

```text
dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S31-01 | В дыму, руки над головой | hero | 85mm lens | — | 131001 |
| S31-02 | Сидя на кубе, нога вытянута | hero | 35mm lens | — | 131002 |
| S31-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 131003 |
| S31-04 | Отражение | core | 50mm lens | — | 131004 |
| S31-05 | Против света | core | 35mm lens | — | 131005 |
| S31-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 131006 |
| S31-07 | В рост, рука в волосах | core | 50mm lens | — | 131007 |
| S31-08 | Деталь | filler | 85mm lens | — | 131008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Ektar 100, tight grain, hard clean blacks
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S31-01 — В дыму, руки над головой

*hero · seed 131001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet, standing in the drifting smoke in the silver set, both arms raised overhead with wrists crossed, ribcage lifted, back arched, chin up, eyes half closed against the light, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, eye level, frontal, full body framing, shot on Kodak Ektar 100, tight grain, hard clean blacks, one hard strobe from the side carving her silhouette out of the smoke, handheld frame tilted a degree or two off level, dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S31-02 — Сидя на кубе, нога вытянута

*hero · seed 131002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet, sitting on the low black cube with one leg extended long and pointed, the other bent, leaning back on both hands, head tipped back and then turned straight into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera, three-quarter front, full body framing, shot on Kodak Ektar 100, tight grain, hard clean blacks, hard strobe from above and behind, smoke glowing, deep black floor, slightly underexposed, shadows crushed a little, dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S31-03 — Прогиб, взгляд через плечо

*core · seed 131003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet, kneeling back on her heels on the low black cube, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Ektar 100, tight grain, hard clean blacks, one hard strobe raking across her through the smoke, a second narrow strobe drawing a bright line down her opposite side, one highlight blown out where the light hits hardest, dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S31-04 — Отражение

*core · seed 131004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet, standing close to a tall sheet of mirror at the edge of the set, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Ektar 100, tight grain, hard clean blacks, one hard strobe raking across her through the smoke, a second narrow strobe drawing a bright line down her opposite side, focus landing a touch behind the eyes, sharpest on the ear, dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S31-05 — Против света

*core · seed 131005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet, standing at the bright edge of the strobe beam with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Kodak Ektar 100, tight grain, hard clean blacks, one hard strobe raking across her through the smoke, a second narrow strobe drawing a bright line down her opposite side, faint haze from a smudge on the front element, dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S31-06 — Полулёжа, нога вытянута

*core · seed 131006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet, reclining back on the low black cube propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Ektar 100, tight grain, hard clean blacks, one hard strobe raking across her through the smoke, a second narrow strobe drawing a bright line down her opposite side, slight motion blur in one hand from a slow shutter, dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S31-07 — В рост, рука в волосах

*core · seed 131007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet, standing tall in the middle of the smoke-filled set, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Ektar 100, tight grain, hard clean blacks, one hard strobe raking across her through the smoke, a second narrow strobe drawing a bright line down her opposite side, subject a little off-centre with one shoulder cropped by the frame edge, dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S31-08 — Деталь

*filler · seed 131008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, liquid silver metallic lingerie set with full opaque lining, smooth structured cups and high-cut briefs, silver star pendant, sleek wet-look hair pulled back, bare feet, cropped detail composition of the metallic fabric edge across her hip catching a hard specular line, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, liquid silver set catching a hard strobe through the smoke, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Ektar 100, tight grain, hard clean blacks, one hard strobe raking across her through the smoke, a second narrow strobe drawing a bright line down her opposite side, mild flare washing one corner of the frame, dark photo studio filled with drifting smoke, single hard strobe head, black seamless floor and backdrop, low black cube, light stands just out of frame, beams visible in the haze, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
