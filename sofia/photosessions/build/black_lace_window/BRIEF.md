# Чёрное кружево у окна (Black Lace at Night)

**ID сессии:** `S17` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 117000

**Референс:** Серия в кружевном белье — гламурный будуарный регистр

**Настроение:** Ночь, город за стеклом, одна лампа. Чёрное кружево и холодный синий контур.

**Подача (слой на каждом кадре):**

```text
lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow
```

## Гардероб (единый для всех кадров)

`Q` — Чёрный кружевной комплект с подкладкой — бра и высокие трусики.

```text
black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet
```

## Локация

Тёмная спальня ночью, панорамное окно, одна тёплая лампа.

```text
dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S17-01 | Против огней города | hero | 35mm lens | — | 117001 |
| S17-02 | На подоконнике, колено поднято | hero | 50mm lens | — | 117002 |
| S17-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 117003 |
| S17-04 | Отражение | core | 50mm lens | — | 117004 |
| S17-05 | Силуэт против света | core | 35mm lens | — | 117005 |
| S17-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 117006 |
| S17-07 | Деталь | filler | 85mm lens | — | 117007 |
| S17-08 | Вид сверху | core | 35mm lens | — | 117008 |
| S17-09 | В рост, рука в волосах | core | 50mm lens | — | 117009 |
| S17-10 | Общий план | core | 24mm wide lens | — | 117010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T, city bokeh halated, grain through the darks
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S17-01 — Против огней города

*hero · seed 117001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, standing full length at the dark window in the black lace set, one forearm raised against the glass above her head, back arched, weight on one hip, head turned to hold the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, three-quarter front angle, full body vertical framing, shot on Cinestill 800T, city bokeh halated, grain through the darks, cool city bokeh behind her rimming the lace, single warm lamp low from the side, handheld frame tilted a degree or two off level, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-02 — На подоконнике, колено поднято

*hero · seed 117002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, sitting up on the wide windowsill with her back against the frame, one knee drawn up and the other leg hanging, one hand in her hair, slow half-lidded look into the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, frontal, full body framing, shot on Cinestill 800T, city bokeh halated, grain through the darks, warm lamp key from inside the room, cold blue window light along her outline, slightly underexposed, shadows crushed a little, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-03 — Прогиб, взгляд через плечо

*core · seed 117003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, kneeling back on her heels on the dark linen bed, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, city bokeh halated, grain through the darks, one warm brass lamp raking low across the lace, cold blue city light drawing her whole outline, one highlight blown out where the light hits hardest, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-04 — Отражение

*core · seed 117004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, standing close to the tall unlit mirror beside the window, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T, city bokeh halated, grain through the darks, one warm brass lamp raking low across the lace, cold blue city light drawing her whole outline, focus landing a touch behind the eyes, sharpest on the ear, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-05 — Силуэт против света

*core · seed 117005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, standing at the floor-to-ceiling city window with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Cinestill 800T, city bokeh halated, grain through the darks, one warm brass lamp raking low across the lace, cold blue city light drawing her whole outline, faint haze from a smudge on the front element, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-06 — Полулёжа, нога вытянута

*core · seed 117006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, reclining back on the dark linen bed propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T, city bokeh halated, grain through the darks, one warm brass lamp raking low across the lace, cold blue city light drawing her whole outline, slight motion blur in one hand from a slow shutter, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-07 — Деталь

*filler · seed 117007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, cropped detail composition of the scalloped lace edge across her hip and her fingers resting there, face out of frame, fingers relaxed and naturally posed, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T, city bokeh halated, grain through the darks, one warm brass lamp raking low across the lace, cold blue city light drawing her whole outline, subject a little off-centre with one shoulder cropped by the frame edge, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-08 — Вид сверху

*core · seed 117008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, lying on her back on the dark linen bed, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Cinestill 800T, city bokeh halated, grain through the darks, one warm brass lamp raking low across the lace, cold blue city light drawing her whole outline, mild flare washing one corner of the frame, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-09 — В рост, рука в волосах

*core · seed 117009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, standing tall in the middle of the dark room, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, city bokeh halated, grain through the darks, one warm brass lamp raking low across the lace, cold blue city light drawing her whole outline, grain heavier in the shadows where the exposure was pushed, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S17-10 — Общий план

*core · seed 117010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, black French lace lingerie set with full opaque lining, delicate scalloped edges, underwired balconette bra and high-waisted lace briefs, silver star pendant, dark hair loose and tousled, bare feet, seen small across the space small against the huge night window, caught mid-movement and not looking at the camera, the room itself carrying the mood, lace lingerie editorial glamour, delicate lace set with full opaque lining, sculpted waist and long legs, soft boudoir light gliding over the lace, assured sensual gaze, black lace reading sharp against the city glow, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Cinestill 800T, city bokeh halated, grain through the darks, one warm brass lamp raking low across the lace, cold blue city light drawing her whole outline, colour a touch cool and uncorrected straight out of camera, dark bedroom at night, floor-to-ceiling window with deep city bokeh, wide stone windowsill, one warm brass lamp, dark linen bed, heavy curtains pushed aside, polished dark floor, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
