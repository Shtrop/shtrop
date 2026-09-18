# Неоновое селфи ночью (Neon Selfie Night)

**ID сессии:** `S03` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 103000

**Референс:** Референс 3 — селфи с прищуром, розовый халат, гейминг-комната с неоном

**Настроение:** Игривая, домашняя, чуть дерзкая. Эстетика фронтальной камеры: лёгкий шум, живая перспектива.

## Гардероб (единый для всех кадров)

`C` — Халат всегда на плечах или приспущен, но кадр остаётся SFW — топ полностью надет.

```text
white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks
```

## Локация

Неон розово-фиолетовый + тёплая свеча. Не выводить читаемый текст в кадре (brand safety).

```text
night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S03-01 | Селфи с подмигиванием (реконструкция референса) | hero | 24mm front-facing phone camera look | — | 103001 |
| S03-02 | Зеркальное селфи в полный рост | core | 26mm phone rear camera look | — | 103002 |
| S03-03 | Селфи за игровым столом в наушниках | core | 24mm front-facing phone camera look | да | 103003 |
| S03-04 | Селфи сверху, лёжа в подушках | core | 24mm front-facing phone camera look | — | 103004 |
| S03-05 | Полулицо крупно, неоновый контур | hero | 24mm front-facing phone camera look | — | 103005 |
| S03-06 | Селфи на фоне неоновой вывески | core | 24mm front-facing phone camera look | — | 103006 |
| S03-07 | Кандид: смеётся за клавиатурой | core | 35mm lens | да | 103007 |
| S03-08 | Селфи с капучино у лица | core | 24mm front-facing phone camera look | да | 103008 |
| S03-09 | Селфи у окна, капюшон халата | core | 24mm front-facing phone camera look | — | 103009 |
| S03-10 | Автопортрет сверху: ноги, ноутбук, кадр в кадре | filler | 24mm front-facing phone camera look | — | 103010 |

Наушники на шее: 3/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S03-01 — Селфи с подмигиванием (реконструкция референса)

*hero · seed 103001*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, handheld arm's-length selfie while leaning back into the pillows on the bed, one arm extended toward the camera, head tilted against the shoulder, one eye winked shut, lips in a soft playful pout, pink robe slipping off both shoulders, 24mm front-facing phone camera look, slightly above eye level, natural selfie perspective with mild wide-angle distortion, chest-up framing, mixed pink and violet neon wash from the left, warm candle glow from the right, cool city window as background bokeh, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-02 — Зеркальное селфи в полный рост

*core · seed 103002*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, full-length mirror selfie standing with the phone held at chest height partially covering her face, hip cocked to one side, free hand tugging the fuzzy robe off one shoulder, relaxed confident posture, 26mm phone rear camera look, eye level, full body framing in the mirror with the neon-lit room reflected behind, pink neon key from behind the camera, violet RGB rim along the arm and robe, mild mirror haze, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-03 — Селфи за игровым столом в наушниках

*core · seed 103003*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, white over-ear headphones resting around her neck, sitting sideways in the white gaming chair with white over-ear headphones on, holding the phone out to one side, knees pulled up onto the seat, making a small peace sign near her cheek, bright open smile, 24mm front-facing phone camera look, slight high angle, waist-up framing with the glowing monitor behind, cool monitor glow on one side of the face, pink RGB strip light on the other, dark room between them, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-04 — Селфи сверху, лёжа в подушках

*core · seed 103004*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, lying on her back among the faux-fur cushions holding the phone directly above her face with both hands, loose strands fanned across the pillow, robe spread open around her like petals, lips slightly parted, sleepy eye contact, 24mm front-facing phone camera look, directly overhead top-down angle, head-and-shoulders framing, soft violet neon from above the bed, warm candle spill on the cheek, gentle falloff into the dark bedding, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-05 — Полулицо крупно, неоновый контур

*hero · seed 103005*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, very close selfie filling the frame with half of her face, one hand pushing loose strands back from the temple, chin slightly down, steady direct eye contact, small knowing smirk, 24mm front-facing phone camera look, extreme close framing, mild lens distortion at the edges, hard pink neon rim along the cheekbone and jaw, magenta catchlights in the eyes, deep shadow on the far side, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-06 — Селфи на фоне неоновой вывески

*core · seed 103006*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, standing selfie turned three-quarter away with the glowing pink neon sign framed over her shoulder, phone held high, free hand adjusting the messy bun, chin lifted, calm cool expression, 24mm front-facing phone camera look, high angle looking down, chest-up framing, saturated pink neon backlight glowing through the loose hair, weak warm fill on the face, heavy color contrast, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-07 — Кандид: смеётся за клавиатурой

*core · seed 103007*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, white over-ear headphones resting around her neck, candid third-person shot of her mid-laugh at the gaming desk, both hands on a low-profile keyboard, headphones on, shoulders hunched forward in excitement, eyes on the monitor and not on the camera, 35mm lens, eye level, side three-quarter angle, waist-up framing, monitor glow as the main key on the face, violet RGB rim from behind, candle warmth in the far background, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-08 — Селфи с капучино у лица

*core · seed 103008*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, white over-ear headphones resting around her neck, cozy selfie holding a ceramic mug of cappuccino up near her cheek with both hands, robe pulled closed around her, shoulders raised in a comfortable shrug, warm soft smile with eyes almost closed, 24mm front-facing phone camera look, eye level, chest-up framing, warm candle key from below the mug, pink neon fill from the side, steam catching the light between them, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-09 — Селфи у окна, капюшон халата

*core · seed 103009*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, selfie beside the dark window with the fuzzy pink robe hood pulled up over the bun, one hand holding the hood edge near her face, leaning her temple against the glass, quiet thoughtful expression, 24mm front-facing phone camera look, eye level, head-and-shoulders framing with the city bokeh behind, low ambient night light, cool blue city reflection on the cheek, faint pink neon from deep in the room, visible low-light grain, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```

### S03-10 — Автопортрет сверху: ноги, ноутбук, кадр в кадре

*filler · seed 103010*

```text
Sofia, 26-year-old woman, warm olive skin, dark brown almost-black hair, defined dark brows, hazel-green eyes, straight nose, full lips, soft oval face with high cheekbones, athletic hourglass figure, tiny beauty mark placement per persona config, white ribbed cotton camisole with tiny pink ditsy floral print and a small pink satin bow at the neckline, light grey drawstring sweatpants, fuzzy soft pink fleece robe worn open and slipping off both shoulders, thin silver chain with small star pendant, dark brown messy high bun with damp loose strands framing the face, dewy natural makeup with glossy lips and flushed cheeks, top-down self-portrait looking down her own body from her eye position, showing crossed legs in grey sweatpants, sock-clad feet, an open laptop and a mug on the bedding, one hand in the frame holding the phone visible in a small mirror at the edge, 24mm front-facing phone camera look, steep top-down point-of-view angle, wide flat-lay style framing, even pink and violet ambient neon over the bedding, warm candle pool in one corner, soft shadows, night bedroom with a gaming setup, ultrawide monitor glowing with a purple sunset wallpaper, white over-ear headphones on a stand, RGB light strips in pink and violet, pink neon sign reading nothing legible on the wall, wall of pinned polaroid photographs, white gaming chair, lit candle, stack of books, plush cushions and cream faux-fur bedding, floor-to-ceiling window with city bokeh, photorealistic editorial photograph, natural skin texture with visible pores and fine detail, realistic subsurface scattering, film-like color grading, sharp focus on eyes, shallow depth of field, high dynamic range, shot on full-frame mirrorless camera, 4k detail
```
