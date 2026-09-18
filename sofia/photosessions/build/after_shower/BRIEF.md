# После душа (After the Shower)

**ID сессии:** `S10` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 110000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Пар, мрамор, свечи. Полотенце и мокрые плечи.

**Подача (слой на каждом кадре):**

```text
steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look
```

## Гардероб (единый для всех кадров)

`J` — Маленькое белое полотенце, придерживается рукой. Мокрая кожа и волосы.

```text
small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot
```

## Локация

Мраморная ванная в пару, запотевшее зеркало, свечи, отдельная ванна.

```text
steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S10-01 | У запотевшего зеркала | hero | 50mm lens | — | 110001 |
| S10-02 | На краю ванны | hero | 35mm lens | — | 110002 |
| S10-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 110003 |
| S10-04 | Отражение | core | 50mm lens | — | 110004 |
| S10-05 | Силуэт против света | core | 35mm lens | — | 110005 |
| S10-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 110006 |
| S10-07 | Деталь | filler | 85mm lens | — | 110007 |
| S10-08 | Вид сверху | core | 35mm lens | — | 110008 |
| S10-09 | В рост, рука в волосах | core | 50mm lens | — | 110009 |
| S10-10 | Общий план | core | 24mm wide lens | — | 110010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T, candle halation, heavy grain in the dark corners
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S10-01 — У запотевшего зеркала

*hero · seed 110001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, standing at the fogged mirror having wiped one stripe clear, towel held closed at the chest, damp shoulders bare, meeting the camera through the cleared stripe of glass, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the mirror, waist-up framing, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight from the basin below, soft glow of steam catching the light, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-02 — На краю ванны

*hero · seed 110002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, sitting on the wide marble edge of the tub, one long leg extended and the other bent, towel high on the thigh, leaning back on one hand, head tilted with a slow look at the lens, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera, three-quarter front angle, full body framing, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, candles clustered low around the tub, cool frosted-window glow behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-03 — Прогиб, взгляд через плечо

*core · seed 110003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, kneeling back on her heels on the wide marble edge of the tub, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight low and close to her skin, soft daylight glow through the frosted window behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-04 — Отражение

*core · seed 110004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, standing close to the fogged bathroom mirror, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight low and close to her skin, soft daylight glow through the frosted window behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-05 — Силуэт против света

*core · seed 110005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, standing at the frosted bathroom window with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight low and close to her skin, soft daylight glow through the frosted window behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-06 — Полулёжа, нога вытянута

*core · seed 110006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, reclining back on the wide marble edge of the tub propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight low and close to her skin, soft daylight glow through the frosted window behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-07 — Деталь

*filler · seed 110007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, cropped detail composition of a water drop running from her shoulder to her collarbone, face out of frame, fingers relaxed and naturally posed, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight low and close to her skin, soft daylight glow through the frosted window behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-08 — Вид сверху

*core · seed 110008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, lying on her back on the wide marble edge of the tub, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight low and close to her skin, soft daylight glow through the frosted window behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-09 — В рост, рука в волосах

*core · seed 110009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, standing tall in the middle of the steamy bathroom floor, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight low and close to her skin, soft daylight glow through the frosted window behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S10-10 — Общий план

*core · seed 110010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, small white bath towel wrapped around her body and held closed at the chest, bare shoulders, bare legs, damp skin, wet hair, silver star pendant, barefoot, seen small across the space beside the freestanding tub, caught mid-movement and not looking at the camera, the room itself carrying the mood, steamy bathroom glamour, small towel held closed at the chest, bare shoulders and long bare legs, damp skin catching the candlelight, slow direct look, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Cinestill 800T, candle halation, heavy grain in the dark corners, warm candlelight low and close to her skin, soft daylight glow through the frosted window behind her, steamy marble bathroom, fogged mirror above a stone basin, freestanding tub, lit candles, brass tap running, folded towels, eucalyptus branch, warm low light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
