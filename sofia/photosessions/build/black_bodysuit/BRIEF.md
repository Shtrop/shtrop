# Чёрное боди в студии (Black Bodysuit Studio)

**ID сессии:** `S11` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 111000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Чистая студия, чёрный фон, один софтбокс. Только фигура и свет.

**Подача (слой на каждом кадре):**

```text
editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze
```

## Гардероб (единый для всех кадров)

`K` — Чёрное боди с глубоким вырезом, высокая посадка, плотная ткань. Чулки.

```text
high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands
```

## Локация

Тёмная студия, бесшовный чёрный фон, один софтбокс, легкая дымка.

```text
dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S11-01 | Свет по контуру | hero | 85mm lens | — | 111001 |
| S11-02 | Портрет в контровом | hero | 85mm portrait lens | — | 111002 |
| S11-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 111003 |
| S11-04 | Отражение | core | 50mm lens | — | 111004 |
| S11-05 | Силуэт против света | core | 35mm lens | — | 111005 |
| S11-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 111006 |
| S11-07 | Деталь | filler | 85mm lens | — | 111007 |
| S11-08 | Вид сверху | core | 35mm lens | — | 111008 |
| S11-09 | В рост, рука в волосах | core | 50mm lens | — | 111009 |
| S11-10 | Общий план | core | 24mm wide lens | — | 111010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S11-01 — Свет по контуру

*hero · seed 111001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, standing in profile turned into the light, back deeply arched, both arms raised overhead with wrists crossed, ribcage lifted, chin up, eyes closed, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, eye level, side profile, full body framing, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one hard softbox edge grazing the whole silhouette, everything else falling to black, handheld frame tilted a degree or two off level, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-02 — Портрет в контровом

*hero · seed 111002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, tight portrait, chin lowered and eyes lifted straight into the lens, one hand resting at her throat, lips parted, sleek hair with loose strands, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm portrait lens, eye level, head-and-shoulders framing, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, hard rim light along the jaw and cheekbone, single soft fill from the front, black background, slightly underexposed, shadows crushed a little, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-03 — Прогиб, взгляд через плечо

*core · seed 111003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, kneeling back on her heels on the low black apple box, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one large softbox raking from camera left, raking across her, leaving real shadow in every hollow, a narrow hard rim light along her opposite side, one highlight blown out where the light hits hardest, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-04 — Отражение

*core · seed 111004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, standing close to the tall studio mirror at the edge of the set, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one large softbox raking from camera left, raking across her, leaving real shadow in every hollow, a narrow hard rim light along her opposite side, focus landing a touch behind the eyes, sharpest on the ear, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-05 — Силуэт против света

*core · seed 111005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, standing at the edge of the black backdrop where the light falls off with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one large softbox raking from camera left, raking across her, leaving real shadow in every hollow, a narrow hard rim light along her opposite side, faint haze from a smudge on the front element, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-06 — Полулёжа, нога вытянута

*core · seed 111006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, reclining back on the low black apple box propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one large softbox raking from camera left, raking across her, leaving real shadow in every hollow, a narrow hard rim light along her opposite side, slight motion blur in one hand from a slow shutter, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-07 — Деталь

*filler · seed 111007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, cropped detail composition of the line of her waist and the edge of the bodysuit against the black, face out of frame, fingers relaxed and naturally posed, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one large softbox raking from camera left, raking across her, leaving real shadow in every hollow, a narrow hard rim light along her opposite side, subject a little off-centre with one shoulder cropped by the frame edge, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-08 — Вид сверху

*core · seed 111008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, lying on her back on the low black apple box, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one large softbox raking from camera left, raking across her, leaving real shadow in every hollow, a narrow hard rim light along her opposite side, mild flare washing one corner of the frame, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-09 — В рост, рука в волосах

*core · seed 111009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, standing tall alone in the middle of the black set, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one large softbox raking from camera left, raking across her, leaving real shadow in every hollow, a narrow hard rim light along her opposite side, grain heavier in the shadows where the exposure was pushed, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S11-10 — Общий план

*core · seed 111010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, high-cut black bodysuit with a plunging neckline, opaque matte fabric, sheer black stockings, silver star pendant, bare feet, hair in a sleek low bun with loose strands, seen small across the space small against the huge black backdrop, caught mid-movement and not looking at the camera, the room itself carrying the mood, editorial bodysuit glamour, high-cut bodysuit with a plunging neckline, long legs in sheer stockings, sculpted shoulders and waist, cool commanding gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Kodak Ektar 100 in the studio, fine tight grain, deep true blacks, one large softbox raking from camera left, raking across her, leaving real shadow in every hollow, a narrow hard rim light along her opposite side, colour a touch cool and uncorrected straight out of camera, dark photo studio, seamless black backdrop, single large softbox, faint atmospheric haze, black apple box, bare concrete floor, deep falloff into black, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
