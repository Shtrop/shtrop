# Чулки и пиджак (Stockings and Blazer)

**ID сессии:** `S16` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 116000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Отельный люкс ночью, бархат и виски. Чулки, боди и чужой пиджак.

**Подача (слой на каждом кадре):**

```text
late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze
```

## Гардероб (единый для всех кадров)

`P` — Чёрные чулки, боди с кружевной отделкой, огромный мужской пиджак с плеч.

```text
sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up
```

## Локация

Тёмный отельный люкс, бархатное кресло, торшер, город за окном.

```text
dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S16-01 | В бархатном кресле | hero | 35mm lens | — | 116001 |
| S16-02 | Чулок, у окна | hero | 50mm lens | — | 116002 |
| S16-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 116003 |
| S16-04 | Отражение | core | 50mm lens | — | 116004 |
| S16-05 | Силуэт против света | core | 35mm lens | — | 116005 |
| S16-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 116006 |
| S16-07 | Деталь | filler | 85mm lens | — | 116007 |
| S16-08 | Вид сверху | core | 35mm lens | — | 116008 |
| S16-09 | В рост, рука в волосах | core | 50mm lens | — | 116009 |
| S16-10 | Общий план | core | 24mm wide lens | — | 116010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T, tungsten cast and grain in the velvet shadows
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S16-01 — В бархатном кресле

*hero · seed 116001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, sitting deep in the velvet armchair with her legs crossed high, blazer hanging open off both shoulders, one arm stretched along the back of the chair, cool amused look at the lens, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, three-quarter front angle, full body framing, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp close on one side, city window glow cool behind the chair, handheld frame tilted a degree or two off level, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-02 — Чулок, у окна

*hero · seed 116002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, standing at the city window with one heel up on the sill, adjusting the lace top of the stocking, blazer sliding down her arms, head turned to hold the lens, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, low angle, side three-quarter, full body framing, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, cool city light silhouetting the leg and the blazer, warm lamp accent from inside the room, slightly underexposed, shadows crushed a little, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-03 — Прогиб, взгляд через плечо

*core · seed 116003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, kneeling back on her heels on the deep velvet armchair, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp light close on one side of her, cool city window light along her opposite edge, one highlight blown out where the light hits hardest, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-04 — Отражение

*core · seed 116004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, standing close to the gilt mirror above the console, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp light close on one side of her, cool city window light along her opposite edge, focus landing a touch behind the eyes, sharpest on the ear, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-05 — Силуэт против света

*core · seed 116005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, standing at the wide city window with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back view, full body vertical framing, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp light close on one side of her, cool city window light along her opposite edge, faint haze from a smudge on the front element, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-06 — Полулёжа, нога вытянута

*core · seed 116006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, reclining back on the deep velvet armchair propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp light close on one side of her, cool city window light along her opposite edge, slight motion blur in one hand from a slow shutter, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-07 — Деталь

*filler · seed 116007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, cropped detail composition of the lace top of the stocking and her hand resting on her thigh, face out of frame, fingers relaxed and naturally posed, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp light close on one side of her, cool city window light along her opposite edge, subject a little off-centre with one shoulder cropped by the frame edge, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-08 — Вид сверху

*core · seed 116008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, lying on her back on the deep velvet armchair, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, directly overhead top-down angle, full body framing, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp light close on one side of her, cool city window light along her opposite edge, mild flare washing one corner of the frame, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-09 — В рост, рука в волосах

*core · seed 116009*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, standing tall beside the armchair with the blazer hanging open, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp light close on one side of her, cool city window light along her opposite edge, grain heavier in the shadows where the exposure was pushed, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S16-10 — Общий план

*core · seed 116010*

```text
Sofia, 26-year-old woman, athletic hourglass figure, sheer black hold-up stockings, black bodysuit with lace trim, oversized men's blazer draped off both shoulders, black heels, silver star pendant, hair loosely pinned up, seen small across the space across the dim hotel suite, caught mid-movement and not looking at the camera, the room itself carrying the mood, late-night glamour, sheer hold-up stockings and a lace-trim bodysuit under an oversized blazer sliding off both shoulders, long legs crossed, cool amused gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 24mm wide lens, eye level, wide environmental full-body shot, shot on Cinestill 800T, tungsten cast and grain in the velvet shadows, warm brass lamp light close on one side of her, cool city window light along her opposite edge, colour a touch cool and uncorrected straight out of camera, dark hotel suite at night, deep green velvet armchair, brass floor lamp, whisky glass on a side table, heavy drapes, wide city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
