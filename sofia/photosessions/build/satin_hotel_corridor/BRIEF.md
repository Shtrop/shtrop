# Сатин в коридоре отеля (Satin Corridor)

**ID сессии:** `S30` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 130000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Коридор отеля ночью, ковёр, бра через равные шаги. Чёрный сатин и сетка.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces
```

## Гардероб (единый для всех кадров)

`AD` — Чёрный сатиновый комплект с подкладкой + чулки в сетку.

```text
black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet
```

## Локация

Длинный коридор отеля ночью, ковёр с рисунком, бра по стенам.

```text
long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S30-01 | Спиной вдоль коридора | hero | 35mm lens | — | 130001 |
| S30-02 | У двери номера | hero | 50mm lens | — | 130002 |
| S30-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 130003 |
| S30-04 | Отражение | core | 50mm lens | — | 130004 |
| S30-05 | Против света | core | 35mm lens | — | 130005 |
| S30-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 130006 |
| S30-07 | В рост, рука в волосах | core | 50mm lens | — | 130007 |
| S30-08 | Деталь | filler | 85mm lens | — | 130008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T, tungsten cast and sconce halation
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S30-01 — Спиной вдоль коридора

*hero · seed 130001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet, standing in the middle of the long corridor with her back to the camera in the black satin set, one hand trailing along the wall, weight on one hip, head turned over her shoulder to the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back view down the corridor, full body framing, shot on Cinestill 800T, tungsten cast and sconce halation, row of warm wall sconces receding behind her, pools of light on the carpet, handheld frame tilted a degree or two off level, long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S30-02 — У двери номера

*hero · seed 130002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet, leaning back against the numbered door with one knee bent and the sole of her foot against it, both hands behind her lower back, chest lifted, cool level stare at the camera, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, tungsten cast and sconce halation, one sconce directly above her throwing hard shadow under the jaw, dark corridor beyond, slightly underexposed, shadows crushed a little, long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S30-03 — Прогиб, взгляд через плечо

*core · seed 130003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet, kneeling back on her heels on the patterned corridor carpet, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, tungsten cast and sconce halation, warm sconce light from directly above her, the receding row of sconces glowing behind her, one highlight blown out where the light hits hardest, long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S30-04 — Отражение

*core · seed 130004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet, standing close to the mirror at the far end of the corridor, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T, tungsten cast and sconce halation, warm sconce light from directly above her, the receding row of sconces glowing behind her, focus landing a touch behind the eyes, sharpest on the ear, long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S30-05 — Против света

*core · seed 130005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet, standing at the lit window at the end of the corridor with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, tungsten cast and sconce halation, warm sconce light from directly above her, the receding row of sconces glowing behind her, faint haze from a smudge on the front element, long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S30-06 — Полулёжа, нога вытянута

*core · seed 130006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet, reclining back on the patterned corridor carpet propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T, tungsten cast and sconce halation, warm sconce light from directly above her, the receding row of sconces glowing behind her, slight motion blur in one hand from a slow shutter, long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S30-07 — В рост, рука в волосах

*core · seed 130007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet, standing tall in a pool of sconce light in the middle of the corridor, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, tungsten cast and sconce halation, warm sconce light from directly above her, the receding row of sconces glowing behind her, subject a little off-centre with one shoulder cropped by the frame edge, long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S30-08 — Деталь

*filler · seed 130008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black satin lingerie set with full opaque lining, structured satin cups and high-waisted satin briefs, black fishnet stockings, silver star pendant, hair loose over one shoulder, bare feet, cropped detail composition of the fishnet pattern stretched across her thigh and her hand resting on it, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, black satin set and fishnet stockings under the corridor sconces, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T, tungsten cast and sconce halation, warm sconce light from directly above her, the receding row of sconces glowing behind her, mild flare washing one corner of the frame, long hotel corridor at night, patterned carpet running away into the distance, warm wall sconces at even intervals, numbered doors, dark wainscoting, one mirror at the far end, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
