# Мокрый шёлк (Wet Silk)

**ID сессии:** `S07` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 107000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Пар, вода, чёрный камень. Тяжёлый мокрый шёлк и прямой взгляд.

**Подача (слой на каждом кадре):**

```text
wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze
```

## Гардероб (единый для всех кадров)

`G` — Короткая чёрная шёлковая комбинация, насквозь мокрая, но плотная и непрозрачная.

```text
short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet
```

## Локация

Душевая за стеклом, чёрный мрамор, пар, латунь. Вода льётся во всех кадрах.

```text
large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S07-01 | Под струёй, взгляд в объектив | hero | 50mm lens | — | 107001 |
| S07-02 | Ладонь на запотевшем стекле | hero | 35mm lens | — | 107002 |
| S07-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 107003 |
| S07-04 | Отражение | core | 50mm lens | — | 107004 |
| S07-05 | Силуэт против света | core | 35mm lens | — | 107005 |
| S07-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 107006 |
| S07-07 | Деталь | filler | 85mm lens | — | 107007 |
| S07-08 | Вид сверху | core | 35mm lens | — | 107008 |
| S07-09 | В рост, рука в волосах | core | 50mm lens | — | 107009 |
| S07-10 | Общий план | core | 24mm wide lens | — | 107010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T, halation around the highlights, grain in the steam
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S07-01 — Под струёй, взгляд в объектив

*hero · seed 107001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, standing directly under the rain shower head with water pouring over her, both hands sliding the soaked hair back from her face, elbows raised, back arched, chin lowered and eyes straight into the lens, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, frontal, thigh-up framing, shot on Cinestill 800T, halation around the highlights, grain in the steam, warm overhead spot burning through the falling water, cool rim off the wet glass behind her, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-02 — Ладонь на запотевшем стекле

*hero · seed 107002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, pressed against the fogged glass from inside the shower, one palm and her cheek flat on the glass, back deeply arched, head turned sideways to hold the lens through the condensation, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, three-quarter front angle, waist-up framing, shot on Cinestill 800T, halation around the highlights, grain in the steam, warm light from behind her inside the shower, cool spill through the fogged glass, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-03 — Прогиб, взгляд через плечо

*core · seed 107003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, kneeling back on her heels on the wet black marble bench, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T, halation around the highlights, grain in the steam, single warm overhead spot cutting through the steam, cool blue light bouncing off the wet glass along her shoulder, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-04 — Отражение

*core · seed 107004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, standing close to the fogged shower glass, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T, halation around the highlights, grain in the steam, single warm overhead spot cutting through the steam, cool blue light bouncing off the wet glass along her shoulder, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-05 — Силуэт против света

*core · seed 107005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, standing at the glass wall of the shower with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Cinestill 800T, halation around the highlights, grain in the steam, single warm overhead spot cutting through the steam, cool blue light bouncing off the wet glass along her shoulder, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-06 — Полулёжа, нога вытянута

*core · seed 107006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, reclining back on the wet black marble bench propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T, halation around the highlights, grain in the steam, single warm overhead spot cutting through the steam, cool blue light bouncing off the wet glass along her shoulder, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-07 — Деталь

*filler · seed 107007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, cropped detail composition of water running down her collarbones and the wet silk strap, face out of frame, fingers relaxed and naturally posed, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T, halation around the highlights, grain in the steam, single warm overhead spot cutting through the steam, cool blue light bouncing off the wet glass along her shoulder, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-08 — Вид сверху

*core · seed 107008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, lying on her back on the wet black marble bench, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Cinestill 800T, halation around the highlights, grain in the steam, single warm overhead spot cutting through the steam, cool blue light bouncing off the wet glass along her shoulder, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-09 — В рост, рука в волосах

*core · seed 107009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, standing tall directly under the rain shower head, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T, halation around the highlights, grain in the steam, single warm overhead spot cutting through the steam, cool blue light bouncing off the wet glass along her shoulder, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S07-10 — Общий план

*core · seed 107010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, short black silk slip dress soaked through and clinging to her body, opaque heavy silk, thin straps slipping off the shoulders, wet hair slicked back, water beading on her skin, silver star pendant, bare feet, seen small across the space behind the fogged glass of the shower, caught mid-movement and not looking at the camera, the room itself carrying the mood, wet-look glamour, soaked opaque silk clinging to every curve, water running over her skin, parted lips, heavy-lidded direct gaze, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Cinestill 800T, halation around the highlights, grain in the steam, single warm overhead spot cutting through the steam, cool blue light bouncing off the wet glass along her shoulder, large walk-in rain shower behind fogged glass, black marble walls and floor, brass fixtures, thick steam, water running down the glass, wet reflections, single warm overhead light, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
