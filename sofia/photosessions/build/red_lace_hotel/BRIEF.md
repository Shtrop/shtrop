# Красное кружево в отеле (Red Lace Suite)

**ID сессии:** `S21` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 121000

**Референс:** Серия в кружевном белье — гламурный будуарный регистр

**Настроение:** Отельный люкс, приглушённый свет, большое зеркало. Красное кружево и уверенность.

**Подача (слой на каждом кадре):**

```text
lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence
```

## Гардероб (единый для всех кадров)

`U` — Красный кружевной комплект с подкладкой, тонкие бретели.

```text
scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet
```

## Локация

Тёмный отельный люкс, большое зеркало, латунные бра, город в окне.

```text
dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S21-01 | В большом зеркале люкса | hero | 35mm lens | — | 121001 |
| S21-02 | На краю кровати, нога на ногу | hero | 50mm lens | — | 121002 |
| S21-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 121003 |
| S21-04 | Отражение | core | 50mm lens | — | 121004 |
| S21-05 | Силуэт против света | core | 35mm lens | — | 121005 |
| S21-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 121006 |
| S21-07 | Деталь | filler | 85mm lens | — | 121007 |
| S21-08 | Вид сверху | core | 35mm lens | — | 121008 |
| S21-09 | В рост, рука в волосах | core | 50mm lens | — | 121009 |
| S21-10 | Общий план | core | 24mm wide lens | — | 121010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T, sconce halation, grain in the deep shadows
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S21-01 — В большом зеркале люкса

*hero · seed 121001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, standing in front of the tall hotel mirror in the red lace set, one hand flat on the glass, hip pushed out, back arched, looking straight past her reflection into the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, three-quarter into the mirror, full body framing, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm sconce light on her front, cool window glow separating her from the dark room, handheld frame tilted a degree or two off level, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-02 — На краю кровати, нога на ногу

*hero · seed 121002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, sitting on the edge of the hotel bed with legs crossed high and back arched, both hands braced behind her on the sheets, chin raised, holding the lens with a level confident gaze, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, sconce halation, grain in the deep shadows, single warm bedside lamp raking across the lace, deep shadow behind her, slightly underexposed, shadows crushed a little, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-03 — Прогиб, взгляд через плечо

*core · seed 121003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, kneeling back on her heels on the crisp hotel bed, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm brass sconce light close on the lace, cool city window light along her back edge, one highlight blown out where the light hits hardest, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-04 — Отражение

*core · seed 121004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, standing close to the tall freestanding hotel mirror, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm brass sconce light close on the lace, cool city window light along her back edge, focus landing a touch behind the eyes, sharpest on the ear, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-05 — Силуэт против света

*core · seed 121005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, standing at the wide curtained city window with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm brass sconce light close on the lace, cool city window light along her back edge, faint haze from a smudge on the front element, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-06 — Полулёжа, нога вытянута

*core · seed 121006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, reclining back on the crisp hotel bed propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm brass sconce light close on the lace, cool city window light along her back edge, slight motion blur in one hand from a slow shutter, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-07 — Деталь

*filler · seed 121007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, cropped detail composition of the embroidered lace edge at her hip and the pendant resting on her collarbone, face out of frame, fingers relaxed and naturally posed, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm brass sconce light close on the lace, cool city window light along her back edge, subject a little off-centre with one shoulder cropped by the frame edge, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-08 — Вид сверху

*core · seed 121008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, lying on her back on the crisp hotel bed, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm brass sconce light close on the lace, cool city window light along her back edge, mild flare washing one corner of the frame, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-09 — В рост, рука в волосах

*core · seed 121009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, standing tall in the middle of the dim suite, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm brass sconce light close on the lace, cool city window light along her back edge, grain heavier in the shadows where the exposure was pushed, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S21-10 — Общий план

*core · seed 121010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, scarlet red lace lingerie set with full opaque lining, delicate embroidered lace, thin straps, matching high-leg lace briefs, silver star pendant, dark hair loose over one shoulder, bare feet, seen small across the space across the long dark hotel suite, caught mid-movement and not looking at the camera, the room itself carrying the mood, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, scarlet lace against dark hotel interiors, unhurried commanding presence, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Cinestill 800T, sconce halation, grain in the deep shadows, warm brass sconce light close on the lace, cool city window light along her back edge, colour a touch cool and uncorrected straight out of camera, dark hotel suite at night, tall freestanding mirror, brass wall sconces, dark wood furniture, crisp white bed with the cover thrown back, heavy curtains, city window glowing behind, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
