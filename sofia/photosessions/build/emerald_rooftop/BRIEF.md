# Изумрудный закат на террасе (Emerald Rooftop Sunset)

**ID сессии:** `S05` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 105000

**Референс:** Развитие референса 1 — та же спортивная линия, но терраса на крыше и канонический изумруд персоны

**Настроение:** Спокойная сила и растяжка вместо железа. Изумруд — канон-палитра Sofia, используем его как акцент сессии.

**Подача (слой на каждом кадре):**

```text
athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze
```

## Гардероб (единый для всех кадров)

`E` — Изумрудный комплект — сигнатурная палитра персоны. Босиком на коврике, обувь только в кадрах у парапета.

```text
tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup
```

## Локация

Закат, открытое небо, город внизу. Свет только естественный, контровой.

```text
private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S05-01 | Наклон вперёд на коврике | hero | 35mm lens | — | 105001 |
| S05-02 | Планка, профиль против неба | core | 50mm lens | — | 105002 |
| S05-03 | Сидит на парапете, город внизу | core | 35mm lens | да | 105003 |
| S05-04 | Растяжка стоя, руки за головой | core | 50mm lens | — | 105004 |
| S05-05 | Поза голубя на коврике | core | 35mm lens | — | 105005 |
| S05-06 | Портрет на закате, изумруд и медь | hero | 85mm portrait lens | — | 105006 |
| S05-07 | Пьёт воду, голова запрокинута | core | 50mm lens | да | 105007 |
| S05-08 | Сидит по-турецки спиной к городу | core | 35mm lens | — | 105008 |
| S05-09 | Деталь: стопы и коврик | filler | 85mm lens | — | 105009 |
| S05-10 | Общий план террасы, силуэт у парапета | core | 24mm wide lens | да | 105010 |

Наушники на шее: 3/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Gold 200, warm golden grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S05-01 — Наклон вперёд на коврике

*hero · seed 105001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, standing forward fold stretch on the yoga mat, legs straight, fingertips reaching the deck, spine long, head turned up toward the camera with direct calm eye contact through the loose strands, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at deck level, three-quarter front angle, full body framing, shot on Kodak Gold 200, warm golden grain, low golden sun directly behind her rimming the shoulders and calves, warm bounce off the wooden deck onto the face, handheld frame tilted a degree or two off level, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-02 — Планка, профиль против неба

*core · seed 105002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, holding a straight-arm plank on the mat, body in one long line, shoulders stacked over wrists, jaw tight, gaze fixed down at the deck, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, ground-level camera, strict side profile, full body framing against the open sky, shot on Kodak Gold 200, warm golden grain, hard contre-jour sunset silhouette with a thin bright rim along the whole body, dark foreground deck, slightly underexposed, shadows crushed a little, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-03 — Сидит на парапете, город внизу

*core · seed 105003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, sitting sideways on the low concrete parapet with one knee pulled up and the other leg hanging, one hand on the concrete, looking out over the skyline in profile, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, side three-quarter angle, full body framing with the city far below, shot on Kodak Gold 200, warm golden grain, warm horizontal sunlight across the face and chest, cool blue shadow on the concrete, one highlight blown out where the light hits hardest, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-04 — Растяжка стоя, руки за головой

*core · seed 105004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, standing tall on the mat with both hands clasped behind her head, elbows wide, ribcage lifted, torso twisted slightly, eyes closed with the sun on her face, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, thigh-up framing, shot on Kodak Gold 200, warm golden grain, direct warm sunset key from camera right, strong modelling on the shoulders and abdomen, olive trees in bokeh behind, focus landing a touch behind the eyes, sharpest on the ear, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-05 — Поза голубя на коврике

*core · seed 105005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, seated pigeon yoga pose on the mat, one leg folded forward and one extended back, chest lifted and back deeply arched, both hands on the front knee, chin raised toward the lens with a steady sensual gaze, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, side three-quarter angle, full body framing, shot on Kodak Gold 200, warm golden grain, soft warm side light, long shadow of her body stretching across the deck toward the camera, faint haze from a smudge on the front element, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-06 — Портрет на закате, изумруд и медь

*hero · seed 105006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, close portrait turned three-quarter to the lens, chin lifted, one hand tucking a loose strand behind the ear, calm confident half-smile with direct eye contact, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm portrait lens, eye level, tight head-and-shoulders framing, city bokeh behind, shot on Kodak Gold 200, warm golden grain, golden hour rim light on the jaw and hair, emerald fabric reading rich against the copper sky, star pendant catching a glint, slight motion blur in one hand from a slow shutter, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-07 — Пьёт воду, голова запрокинута

*core · seed 105007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, standing on the deck drinking from the glass carafe, head tipped back, throat extended, free hand on her hip, eyes closed, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, three-quarter front, waist-up framing, shot on Kodak Gold 200, warm golden grain, backlit sunset flare through the glass carafe, warm rim along the jawline and arm, subject a little off-centre with one shoulder cropped by the frame edge, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-08 — Сидит по-турецки спиной к городу

*core · seed 105008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, kneeling upright in the center of the mat with her back to the skyline, spine arched, both hands sweeping the loose strands back from her face, elbows wide, holding direct eye contact with the camera, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, frontal, full body framing, shot on Kodak Gold 200, warm golden grain, strong backlight from the setting sun behind her head creating a halo through the loose strands, soft reflector fill on the face, mild flare washing one corner of the frame, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-09 — Деталь: стопы и коврик

*filler · seed 105009*

```text
Sofia, 26-year-old woman, athletic hourglass figure, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, cropped detail of her bare feet and shins on the sage yoga mat mid-stretch, toes flexed, one hand reaching down into the frame toward the ankle, face out of shot, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, shallow depth of field, shot on Kodak Gold 200, warm golden grain, low warm sun skimming the deck texture, fine grain of the mat and wood visible, grain heavier in the shadows where the exposure was pushed, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S05-10 — Общий план террасы, силуэт у парапета

*core · seed 105010*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, tight deep emerald green seamless ribbed sports bra with a plunging neckline with thin straps, matching emerald high-waisted leggings, bare feet, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, clean bare skin with visible texture, no heavy makeup, standing small at the far parapet with a towel over one shoulder, back to the camera, looking out at the city as the sun drops behind the skyline, athletic glamour, emerald set hugging every line of the figure, toned waist and long legs emphasised, sheen of sweat on the skin, assured sensual gaze, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 24mm wide lens, eye level, wide environmental shot showing the whole terrace, mat and string lights, shot on Kodak Gold 200, warm golden grain, near-silhouette against a burning orange and violet sky, deck falling into cool shadow, warm flare across the lens, colour a touch cool and uncorrected straight out of camera, private rooftop terrace at sunset, charcoal wooden deck, sage green yoga mat, low concrete parapet overlooking a wide city skyline, olive trees in large concrete planters, rolled towel, glass carafe of water with lemon, string lights strung overhead not yet lit, warm dust haze in the air, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
