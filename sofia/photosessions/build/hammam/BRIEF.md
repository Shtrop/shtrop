# Хаммам (Hammam Steam)

**ID сессии:** `S12` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 112000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Мрамор, пар, арочные окна. Льняная простыня и жар.

**Подача (слой на каждом кадре):**

```text
steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes
```

## Гардероб (единый для всех кадров)

`L` — Льняная простыня, обёрнута и заправлена на груди. Влажная кожа.

```text
white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant
```

## Локация

Мраморный хаммам, пар, латунные чаши, свет через арочные окна.

```text
marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S12-01 | На мраморной плите | hero | 35mm lens | — | 112001 |
| S12-02 | Вода из латунной чаши | hero | 50mm lens | — | 112002 |
| S12-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 112003 |
| S12-04 | Отражение | core | 50mm lens | — | 112004 |
| S12-05 | Силуэт против света | core | 35mm lens | — | 112005 |
| S12-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 112006 |
| S12-07 | Деталь | filler | 85mm lens | — | 112007 |
| S12-08 | Вид сверху | core | 35mm lens | — | 112008 |
| S12-09 | В рост, рука в волосах | core | 50mm lens | — | 112009 |
| S12-10 | Общий план | core | 24mm wide lens | — | 112010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Fujifilm Pro 400H, flat humid tones and soft grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S12-01 — На мраморной плите

*hero · seed 112001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, lying on her side along the warm marble slab, linen draped low across her hip, propped up on one elbow with the other hand on the stone, languid direct gaze through the steam, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at slab level, side three-quarter angle, full body framing, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of window light cutting down through the steam onto her body, wet marble glow underneath, handheld frame tilted a degree or two off level, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-02 — Вода из латунной чаши

*hero · seed 112002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, kneeling on the marble, pouring water from a brass bowl over her own shoulder, head tipped back, eyes closed, linen clinging where the water runs, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, three-quarter front angle, waist-up framing, shot on Fujifilm Pro 400H, flat humid tones and soft grain, backlit steam behind her, warm daylight glinting off the brass and the running water, slightly underexposed, shadows crushed a little, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-03 — Прогиб, взгляд через плечо

*core · seed 112003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, kneeling back on her heels on the warm marble slab, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of daylight cutting down through the steam, soft glow bouncing off the wet marble around her, one highlight blown out where the light hits hardest, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-04 — Отражение

*core · seed 112004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, standing close to the polished wet marble wall, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of daylight cutting down through the steam, soft glow bouncing off the wet marble around her, focus landing a touch behind the eyes, sharpest on the ear, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-05 — Силуэт против света

*core · seed 112005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, standing at the arched window pouring light through the steam with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of daylight cutting down through the steam, soft glow bouncing off the wet marble around her, faint haze from a smudge on the front element, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-06 — Полулёжа, нога вытянута

*core · seed 112006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, reclining back on the warm marble slab propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of daylight cutting down through the steam, soft glow bouncing off the wet marble around her, slight motion blur in one hand from a slow shutter, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-07 — Деталь

*filler · seed 112007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, cropped detail composition of beads of condensation on her shoulder and the edge of the linen, face out of frame, fingers relaxed and naturally posed, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of daylight cutting down through the steam, soft glow bouncing off the wet marble around her, subject a little off-centre with one shoulder cropped by the frame edge, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-08 — Вид сверху

*core · seed 112008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, lying on her back on the warm marble slab, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of daylight cutting down through the steam, soft glow bouncing off the wet marble around her, mild flare washing one corner of the frame, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-09 — В рост, рука в волосах

*core · seed 112009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, standing tall in the middle of the steam-filled chamber, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of daylight cutting down through the steam, soft glow bouncing off the wet marble around her, grain heavier in the shadows where the exposure was pushed, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S12-10 — Общий план

*core · seed 112010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white linen sheet wrapped around her body and tucked at the chest, bare shoulders and bare legs, skin damp and glowing from the heat, hair pinned up with damp strands escaping, no jewellery but the silver star pendant, seen small across the space across the empty marble chamber, caught mid-movement and not looking at the camera, the room itself carrying the mood, steam-room glamour, linen sheet wrapped low and tucked at the chest, bare shoulders, back and legs, skin damp with heat, languid half-closed eyes, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Fujifilm Pro 400H, flat humid tones and soft grain, shafts of daylight cutting down through the steam, soft glow bouncing off the wet marble around her, colour a touch cool and uncorrected straight out of camera, marble hammam chamber, thick steam, warm stone slab in the centre, brass bowls of water, arched windows throwing dappled light through the vapour, worn grey-veined marble, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
