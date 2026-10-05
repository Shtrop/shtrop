# Белая рубашка (His White Shirt)

**ID сессии:** `S09` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 109000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Утро после. Только его рубашка, смятое белое бельё, ветер в занавесках.

**Подача (слой на каждом кадре):**

```text
morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze
```

## Гардероб (единый для всех кадров)

`I` — Огромная мужская рубашка на голое тело — расстёгнута низко, но закрывает.

```text
oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair
```

## Локация

Спальня утром, смятое белое бельё, тюль на ветру.

```text
sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S09-01 | В окне, занавеска вокруг ног | hero | 35mm lens | — | 109001 |
| S09-02 | На кровати, рубашка с плеча | hero | 50mm lens | — | 109002 |
| S09-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 109003 |
| S09-04 | Отражение | core | 50mm lens | — | 109004 |
| S09-05 | Силуэт против света | core | 35mm lens | — | 109005 |
| S09-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 109006 |
| S09-07 | Деталь | filler | 85mm lens | — | 109007 |
| S09-08 | Вид сверху | core | 35mm lens | — | 109008 |
| S09-09 | В рост, рука в волосах | core | 50mm lens | — | 109009 |
| S09-10 | Общий план | core | 24mm wide lens | — | 109010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Portra 400, airy highlights and gentle grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S09-01 — В окне, занавеска вокруг ног

*hero · seed 109001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, standing in the open window with the sheer curtain lifting around her legs, one hand gripping the frame above her head so the shirt falls open, other hand on her hip, eyes into the lens, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, frontal, full body vertical framing, shot on Kodak Portra 400, airy highlights and gentle grain, strong backlight through the curtain haloing her whole silhouette, warm fill off the white linen, handheld frame tilted a degree or two off level, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-02 — На кровати, рубашка с плеча

*hero · seed 109002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, kneeling on the rumpled bed with the shirt slipping off one shoulder, both hands pushing through her tousled hair, elbows wide, chin down and eyes up into the lens, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, frontal, thigh-up framing, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning window light wrapping from camera left, warm linen bounce under the jaw, slightly underexposed, shadows crushed a little, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-03 — Прогиб, взгляд через плечо

*core · seed 109003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, kneeling back on her heels on the rumpled white linen bed, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning sun filtered through the sheer curtain, warm bounce off the white linen filling the shadows, one highlight blown out where the light hits hardest, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-04 — Отражение

*core · seed 109004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, standing close to the tall bedroom mirror, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning sun filtered through the sheer curtain, warm bounce off the white linen filling the shadows, focus landing a touch behind the eyes, sharpest on the ear, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-05 — Силуэт против света

*core · seed 109005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, standing at the open window with the curtain lifting around her with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back view, full body vertical framing, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning sun filtered through the sheer curtain, warm bounce off the white linen filling the shadows, faint haze from a smudge on the front element, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-06 — Полулёжа, нога вытянута

*core · seed 109006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, reclining back on the rumpled white linen bed propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning sun filtered through the sheer curtain, warm bounce off the white linen filling the shadows, slight motion blur in one hand from a slow shutter, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-07 — Деталь

*filler · seed 109007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, cropped detail composition of the open collar of the shirt and the pendant against her skin, face out of frame, fingers relaxed and naturally posed, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning sun filtered through the sheer curtain, warm bounce off the white linen filling the shadows, subject a little off-centre with one shoulder cropped by the frame edge, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-08 — Вид сверху

*core · seed 109008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, lying on her back on the rumpled white linen bed, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, directly overhead top-down angle, full body framing, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning sun filtered through the sheer curtain, warm bounce off the white linen filling the shadows, mild flare washing one corner of the frame, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-09 — В рост, рука в волосах

*core · seed 109009*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, standing tall barefoot in the middle of the sunlit floor, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning sun filtered through the sheer curtain, warm bounce off the white linen filling the shadows, grain heavier in the shadows where the exposure was pushed, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S09-10 — Общий план

*core · seed 109010*

```text
Sofia, 26-year-old woman, athletic hourglass figure, oversized white cotton men's shirt worn on bare skin, unbuttoned low but still covering her, sleeves rolled up, hem falling to the top of her thighs, long bare legs, silver star pendant, tousled loose hair, seen small across the space by the far window of the bedroom, caught mid-movement and not looking at the camera, the room itself carrying the mood, morning-after glamour, oversized shirt open low and slipping off one shoulder, long bare legs, tousled hair, sleepy heavy-lidded gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 24mm wide lens, eye level, wide environmental full-body shot, shot on Kodak Portra 400, airy highlights and gentle grain, soft morning sun filtered through the sheer curtain, warm bounce off the white linen filling the shadows, colour a touch cool and uncorrected straight out of camera, sunlit bedroom in the morning, rumpled white linen bed, sheer white curtains lifting in the breeze, coffee cup on the nightstand, warm oak floor, dust in the light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
