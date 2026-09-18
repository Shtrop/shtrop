# Бассейн на закате (Poolside Sunset)

**ID сессии:** `S08` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 108000

**Референс:** Максимальный гламурный регистр в рамках одетого кадра

**Настроение:** Вилла, инфинити-бассейн, закат над океаном. Мокрая кожа и золото.

**Подача (слой на каждом кадре):**

```text
swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality
```

## Гардероб (единый для всех кадров)

`H` — Чёрное бикини на завязках, высокая посадка. Мокрая кожа, мокрые волосы.

```text
tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes
```

## Локация

Терраса виллы, инфинити-бассейн, океан. Только естественный закатный свет.

```text
infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S08-01 | Выходит из воды | hero | 50mm lens | — | 108001 |
| S08-02 | На бортике, прогиб | hero | 35mm lens | — | 108002 |
| S08-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 108003 |
| S08-04 | Отражение | core | 50mm lens | — | 108004 |
| S08-05 | Силуэт против света | core | 35mm lens | — | 108005 |
| S08-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 108006 |
| S08-07 | Деталь | filler | 85mm lens | — | 108007 |
| S08-08 | Вид сверху | core | 35mm lens | — | 108008 |
| S08-09 | В рост, рука в волосах | core | 50mm lens | — | 108009 |
| S08-10 | Общий план | core | 24mm wide lens | — | 108010 |

Наушники на шее: 0/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Gold 200, sun-bleached warm tones and visible grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S08-01 — Выходит из воды

*hero · seed 108001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, rising out of the pool on the steps with water streaming off her body, one hand sweeping the wet hair back, hip pushed out, head tipped and holding direct eye contact, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, low angle from the deck, frontal, thigh-up framing, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun blazing off the wet skin, shimmering water reflections from below, handheld frame tilted a degree or two off level, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-02 — На бортике, прогиб

*hero · seed 108002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, lying back along the warm travertine edge propped on both elbows, one knee raised high and the other leg stretched into the water, ribcage lifted, face turned up to the sun then to the lens, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at deck level, three-quarter angle, full body framing, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, raking sunset light along the whole length of her body, warm bounce off the pale stone, slightly underexposed, shadows crushed a little, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-03 — Прогиб, взгляд через плечо

*core · seed 108003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, kneeling back on her heels on the warm travertine pool edge, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun raking across her body, shimmering light reflected up off the pool water, one highlight blown out where the light hits hardest, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-04 — Отражение

*core · seed 108004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, standing close to the still mirror-like water surface, one hand resting on the surface, hip pushed out, chin lowered, holding her own gaze while the camera catches her and the reflection at once, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun raking across her body, shimmering light reflected up off the pool water, focus landing a touch behind the eyes, sharpest on the ear, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-05 — Силуэт против света

*core · seed 108005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, standing at the infinity edge of the pool with one forearm raised against the frame, weight settled on one hip, back to the camera, long line of the spine on show, looking away into the light, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, eye level, back view, full body vertical framing, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun raking across her body, shimmering light reflected up off the pool water, faint haze from a smudge on the front element, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-06 — Полулёжа, нога вытянута

*core · seed 108006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, reclining back on the warm travertine pool edge propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun raking across her body, shimmering light reflected up off the pool water, slight motion blur in one hand from a slow shutter, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-07 — Деталь

*filler · seed 108007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, cropped detail composition of water beading on her hip and the bikini tie at her side, face out of frame, fingers relaxed and naturally posed, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun raking across her body, shimmering light reflected up off the pool water, subject a little off-centre with one shoulder cropped by the frame edge, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-08 — Вид сверху

*core · seed 108008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, lying on her back on the warm travertine pool edge, one arm thrown above her head, the other hand resting on her waist, hair fanned out, knees softly bent, eyes lifted to the lens, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 35mm lens, directly overhead top-down angle, full body framing, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun raking across her body, shimmering light reflected up off the pool water, mild flare washing one corner of the frame, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-09 — В рост, рука в волосах

*core · seed 108009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, standing tall waist-deep on the pool steps, one hand pushing back through her hair with the elbow raised, weight shifted onto one leg so the hip breaks the line, chin down and eyes up into the lens, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun raking across her body, shimmering light reflected up off the pool water, grain heavier in the shadows where the exposure was pushed, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S08-10 — Общий план

*core · seed 108010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tiny black string bikini with high-cut bottoms, opaque fabric, wet skin, wet hair pushed back from her face, thin gold anklet, silver star pendant, no shoes, seen small across the space at the far end of the long pool, caught mid-movement and not looking at the camera, the room itself carrying the mood, swimwear glamour, tiny high-cut bikini, long legs and toned waist fully on show, wet golden skin, confident unhurried sensuality, real human skin with visible pores and fine peach fuzz, faint freckles and small blemishes left unretouched, uneven natural skin tone with faint redness at the nose, knuckles and knees, shine only on the T-zone where skin is really oily, fine lines at the corners of the eyes, natural asymmetry between the two halves of the face, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman rather than an idealised figure, 24mm wide lens, eye level, wide environmental full-body shot, shot on Kodak Gold 200, sun-bleached warm tones and visible grain, low golden sun raking across her body, shimmering light reflected up off the pool water, colour a touch cool and uncorrected straight out of camera, infinity pool on a villa terrace at sunset, warm travertine deck, palm shadows across the stone, wet footprints, rolled white towel, glass on the pool edge, ocean horizon glowing orange, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
