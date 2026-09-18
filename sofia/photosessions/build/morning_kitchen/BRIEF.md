# Утро на кухне с капучино (Morning Kitchen Cappuccino)

**ID сессии:** `S04` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 104000

**Референс:** Развитие референса 2 и 3 — домашняя мягкая эстетика, но утренний свет вместо ночного

**Настроение:** Сонная, тёплая, только проснулась. Растрёпанная, босиком, без макияжа. Капучино — сигнатура персоны.

**Подача (слой на каждом кадре):**

```text
intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality
```

## Гардероб (единый для всех кадров)

`D` — Худи всегда спущено с одного плеча, под ним видна бретель топа. Босиком в носках, без обуви.

```text
oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness
```

## Локация

Утренний свет через тюль, много белого и дерева. Держать мягкие тени и лёгкую дымку.

```text
bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S04-01 | Первый глоток у окна | hero | 50mm lens | — | 104001 |
| S04-02 | Сидит на столешнице, ноги свесив | core | 35mm lens | — | 104002 |
| S04-03 | Тянется за кружкой на полке | core | 35mm lens | — | 104003 |
| S04-04 | Кофемашина, пар, ожидание | core | 50mm lens | да | 104004 |
| S04-05 | Деталь: руки и чашка | filler | 85mm lens | — | 104005 |
| S04-06 | Сидит на полу у шкафа | core | 35mm lens | — | 104006 |
| S04-07 | Утренний портрет без макияжа | hero | 85mm portrait lens | — | 104007 |
| S04-08 | Поливает зелень на подоконнике | core | 50mm lens | да | 104008 |
| S04-09 | Танцует босиком по кухне | core | 24mm wide lens | да | 104009 |
| S04-10 | Общий план кухни через дверной проём | core | 35mm lens | — | 104010 |

Наушники на шее: 3/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S04-01 — Первый глоток у окна

*hero · seed 104001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, standing at the kitchen window holding a large ceramic mug of cappuccino with both hands close to her chest, shoulders hunched in comfort, eyes half closed mid-sip, hoodie slipping off one shoulder, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 50mm lens, eye level, three-quarter front angle, waist-up framing, soft diffused morning sunlight through sheer curtains, gentle wraparound fill, warm haze and visible steam, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-02 — Сидит на столешнице, ноги свесив

*core · seed 104002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, sitting up on the marble countertop with legs dangling and ankles crossed, one hand braced on the counter, the other holding the mug on her knee, head tilted with a lazy smile toward the camera, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 35mm lens, slightly low angle, frontal, full body framing, bright window backlight behind her, warm bounce off the white marble filling the face, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-03 — Тянется за кружкой на полке

*core · seed 104003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, stretching up on tiptoes to reach a ceramic mug on the top open shelf, back arched, hoodie riding up slightly, face in profile looking up at the shelf, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 35mm lens, eye level, side three-quarter angle, full body framing, side window light raking across the shelves, long soft shadows on the wall, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-04 — Кофемашина, пар, ожидание

*core · seed 104004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, white over-ear headphones resting around her neck, leaning forward with both forearms on the counter beside the espresso machine, back arched and hips pushed back, watching the coffee pour, head turned to the camera with a slow sleepy look, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 50mm lens, eye level, side three-quarter angle, waist-up framing, warm kitchen lamp mixing with cool window light, steam catching a highlight above the cup, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-05 — Деталь: руки и чашка

*filler · seed 104005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, cropped detail of both hands wrapped around the warm ceramic mug on the marble counter, hoodie sleeves pulled over the palms, star pendant hanging into frame, face out of shot, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 85mm lens, close detail framing, very shallow depth of field, soft window key from the left, gentle specular highlights on the glaze of the mug, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-06 — Сидит на полу у шкафа

*core · seed 104006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, sitting on the warm oak floor with her back against the lower cabinets, one long bare leg extended and the other knee drawn up, hoodie slipping off the shoulder, mug on her knee, head tipped back with eyes half closed, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 35mm lens, low camera at floor level, frontal, full body framing, a single warm shaft of morning sun falling across her face and the floor, rest of the kitchen in soft shade, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-07 — Утренний портрет без макияжа

*hero · seed 104007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, close portrait leaning against the door frame, loose strands across the cheek, chin lowered, sleepy soft eye contact with a barely-there smile, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 85mm portrait lens, eye level, tight head-and-shoulders framing, creamy background bokeh, large soft window key, natural skin texture visible, warm catchlight in both eyes, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-08 — Поливает зелень на подоконнике

*core · seed 104008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, white over-ear headphones resting around her neck, standing at the windowsill watering the potted herbs from a small glass, weight on one hip, free hand touching a leaf, looking down at the plants, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 50mm lens, eye level, side profile, thigh-up framing, strong backlight through the curtain rimming her profile and the plants, cool shade in the foreground, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-09 — Танцует босиком по кухне

*core · seed 104009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, white over-ear headphones resting around her neck, mid-motion barefoot-in-socks spin across the kitchen floor, one arm raised, hoodie flaring, hair strands flying, laughing with her eyes shut, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 24mm wide lens, low angle, wide full-body framing with slight motion blur in the limbs, bright morning wash across the whole room, warm bounce from the oak floor, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S04-10 — Общий план кухни через дверной проём

*core · seed 104010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, oversized cream cotton hoodie slipping far off one bare shoulder, white ribbed boxer-style sleep shorts, slouchy white crew socks, thin silver chain with small star pendant, dark brown messy high bun with loose strands, bare face no-makeup look with soft morning puffiness, seen small from the hallway standing at the far counter with her back to the camera, pouring milk into the cup, morning routine caught from a distance, intimate just-woken mood, oversized hoodie slipping far off one shoulder, long bare legs, sleepy bedroom eyes, soft unguarded sensuality, 35mm lens, eye level, framed through the doorway, wide environmental full-body shot, dark hallway foreground framing a bright sunlit kitchen, strong luminance contrast between the two, bright modern loft kitchen in early morning, white marble countertop, matte black espresso machine, open shelving with ceramic mugs, tall window with sheer white curtains, potted herbs on the sill, wooden cutting board, glass jar of coffee beans, warm oak floor, soft steam in the air, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
