# Золотой час в зале (Golden Hour Gym)

**ID сессии:** `S01` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 101000

**Референс:** Референс 1 — тяга гантели в наклоне, панорамный зал на закате

**Настроение:** Собранная, потная, уверенная. Без улыбки в хиро-кадрах, взгляд в объектив.

**Подача (слой на каждом кадре):**

```text
athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact
```

## Гардероб (единый для всех кадров)

`A` — Один и тот же комплект во всех 10 кадрах. Пыльно-сиреневый топ + светло-серые широкие джоггеры.

```text
tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin
```

## Локация

Одна локация, время — закат. Свет держать тёплым и контровым во всех кадрах.

```text
upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S01-01 | Тяга гантели в наклоне (реконструкция референса) | hero | 35mm lens | — | 101001 |
| S01-02 | Та же тяга, профиль снизу | core | 50mm lens | — | 101002 |
| S01-03 | Пауза на скамье, наушники на шее | core | 50mm lens | да | 101003 |
| S01-04 | У стойки с гантелями, спиной к камере | core | 35mm lens | — | 101004 |
| S01-05 | Выпад с гантелями, широкий план зала | core | 24mm wide lens | — | 101005 |
| S01-06 | У силовой рамы, полуулыбка | core | 50mm lens | да | 101006 |
| S01-07 | Крупный портрет, контровой свет | hero | 85mm portrait lens | — | 101007 |
| S01-08 | Пол, шейкер, контровой закат | core | 35mm lens | — | 101008 |
| S01-09 | Растяжка-силуэт у панорамного окна | core | 50mm lens | — | 101009 |
| S01-10 | Финал сессии: полотенце на шее, шаг в камеру | core | 35mm lens | да | 101010 |

Наушники на шее: 3/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S01-01 — Тяга гантели в наклоне (реконструкция референса)

*hero · seed 101001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, bent-over single-arm dumbbell row, torso hinged forward about 45 degrees, right palm braced flat on the towel-covered bench, left hand gripping a heavy black dumbbell pulled up to the hip, elbow high and back, spine long, legs staggered, head lifted with direct intense eye contact into the lens, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 35mm lens, chest-level eye line, three-quarter front angle, full body vertical framing, warm low sunset backlight through the windows rimming the shoulders and arms, soft bounced fill on the face, glossy highlights on collarbones, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-02 — Та же тяга, профиль снизу

*core · seed 101002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, same bent-over single-arm dumbbell row captured at the top of the pull, shoulder blade retracted, forearm tensed, looking down at the floor in concentration, loose strands falling forward, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 50mm lens, low camera placed near floor level, strict side profile, mid-body to head framing, strong contre-jour sunset flare from the windows, deep shadows in the foreground, warm amber rim on the back and arm, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-03 — Пауза на скамье, наушники на шее

*core · seed 101003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, white over-ear headphones resting around her neck, sitting on the edge of the flat bench, elbows on knees, hands loosely wrapping a fabric lifting strap, head tilted down, eyes lowered, quiet focus between sets, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 50mm lens, slightly above eye level, frontal, waist-up framing, warm window light from camera left, gentle falloff into the dark gym on the right, catchlight in the lowered eyes, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-04 — У стойки с гантелями, спиной к камере

*core · seed 101004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, standing at the dumbbell rack with back three-quarter to camera, right arm reaching out to lift a dumbbell off the rack, weight shifted onto one hip, head turned in profile toward the weights, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 35mm lens, eye level, three-quarter back angle, full body vertical framing, sunset window light from the far side silhouetting the arm, cool ambient fill from ceiling spots on the back, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-05 — Выпад с гантелями, широкий план зала

*core · seed 101005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, deep split-squat lunge holding a dumbbell in each hand at her sides, front knee stacked over ankle, back heel lifted, torso upright, jaw set, gaze fixed forward past the lens, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 24mm wide lens, low angle, wide full-body framing showing the scale of the gym and the city windows, broad golden hour wash across the floor, long shadows stretching toward camera, warm haze in the air, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-06 — У силовой рамы, полуулыбка

*core · seed 101006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, white over-ear headphones resting around her neck, leaning sideways against the squat rack, one forearm resting on the barbell, ankles crossed, chest rising from exertion, faint half-smile with direct eye contact, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 50mm lens, eye level, frontal, thigh-up framing, warm key from the window camera right, soft silver bounce fill, sweat catching the highlights on the shoulders, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-07 — Крупный портрет, контровой свет

*hero · seed 101007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, close portrait, chin slightly lowered, looking straight up into the lens from under the brows, damp strands stuck to the temple, lips parted from breathing, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 85mm portrait lens, eye level, tight head-and-shoulders framing, creamy background bokeh, hard golden rim light outlining the jaw and the loose hair, soft warm fill on the face, star pendant catching a specular glint, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-08 — Пол, шейкер, контровой закат

*core · seed 101008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, sitting on the floor beside the rolled yoga mat, legs extended and ankles crossed, one hand behind for support, the other lifting the transparent shaker bottle toward her mouth, head tipped back slightly, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 35mm lens, low camera at floor level, three-quarter front angle, full body framing, direct backlight from the sunset windows, lens flare across the frame, warm bounce off the tile floor onto the face, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-09 — Растяжка-силуэт у панорамного окна

*core · seed 101009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, standing facing the window in a long overhead stretch, both arms raised and wrists crossed, torso elongated, weight on one leg, head tilted back looking at the skyline, shot from behind, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 50mm lens, eye level, back view, full body vertical framing against the window, near-silhouette against the burning orange sky, thin warm rim along the arms and shoulders, dark gym interior around her, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S01-10 — Финал сессии: полотенце на шее, шаг в камеру

*core · seed 101010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, tight dusty mauve seamless sports bra with a deep scoop neckline with thin spaghetti straps, oversized light heather grey wide-leg cotton sweatpants with white drawstring, white low-profile sneakers, thin silver chain with small star pendant, dark brown messy high bun with damp loose face-framing strands, no makeup look with glossy skin, white over-ear headphones resting around her neck, walking toward the camera with the grey towel draped around her neck, both hands holding the towel ends, mid-stride, chin up, calm satisfied expression with direct eye contact, athletic glamour mood, deep scoop neckline of the sports bra, toned waist and shoulders on display, sweat-glossed skin catching the light, strong arched posture, direct sultry eye contact, 35mm lens, slightly low angle, frontal, knee-up framing with motion-blurred gym background, warm sunset flare blooming behind her shoulder, soft frontal fill, glowing dust in the air, upscale rooftop gym at golden hour, floor-to-ceiling windows overlooking a hazy city skyline, black rubber dumbbell rack, matte black squat rack, large potted monstera and palm plants, dark grey tile floor with soft reflections, rolled purple yoga mat, transparent shaker bottle, black leather flat bench with a dark grey towel, tasteful suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing that emphasises her hourglass figure, dewy glossy skin, soft sculpting light on the curves, confident alluring presence, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
