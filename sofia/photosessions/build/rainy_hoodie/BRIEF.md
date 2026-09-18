# Дождливый день в худи (Rainy Day Hoodie)

**ID сессии:** `S06` · **Кадров:** 10 · **Формат:** 4:5 · **Base seed:** 106000

**Референс:** Развитие референса 3 — та же селфи-эстетика и наушники, но дождь за стеклом вместо неона

**Настроение:** Меланхоличная и уютная. Дождь по стеклу, приглушённый свет, наушники — канон-маркер, здесь используем по максимуму.

**Подача (слой на каждом кадре):**

```text
cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look
```

## Гардероб (единый для всех кадров)

`F` — Серый меланж на всех кадрах. Молния худи наполовину — под ней всегда белый топ, кадр остаётся SFW.

```text
cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup
```

## Локация

Холодный серый дневной свет + одна тёплая лампа. Дождь на стекле обязателен в кадрах у окна.

```text
quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S06-01 | На подоконнике, наушники, дождь по стеклу | hero | 35mm lens | да | 106001 |
| S06-02 | Рисует пальцем по запотевшему стеклу | core | 50mm lens | да | 106002 |
| S06-03 | Селфи в приглушённом свете | core | 24mm front-facing phone camera look | да | 106003 |
| S06-04 | Ставит пластинку | core | 50mm lens | — | 106004 |
| S06-05 | Портрет у окна, капли на стекле в расфокусе | hero | 85mm portrait lens | — | 106005 |
| S06-06 | Лежит на полу с книгой | core | 35mm lens | да | 106006 |
| S06-07 | Стоит у окна, худи на плече | core | 50mm lens | — | 106007 |
| S06-08 | Деталь: наушники и цепочка | filler | 85mm lens | да | 106008 |
| S06-09 | Танцует одна под пластинку | core | 35mm lens | да | 106009 |
| S06-10 | Общий план комнаты в дождь | core | 24mm wide lens | да | 106010 |

Наушники на шее: 7/10 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Fujifilm Pro 400H, cool muted greens and fine grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S06-01 — На подоконнике, наушники, дождь по стеклу

*hero · seed 106001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, sitting sideways in the deep window seat with knees pulled up to her chest, white over-ear headphones on, forehead almost touching the rain-streaked glass, head turned toward the camera with a quiet unsmiling gaze, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, three-quarter front angle, full body framing in the window niche, shot on Fujifilm Pro 400H, cool muted greens and fine grain, cold grey daylight from the window as the key, single warm lamp glowing from deep in the room, rain shadows dappling her face, handheld frame tilted a degree or two off level, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-02 — Рисует пальцем по запотевшему стеклу

*core · seed 106002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, kneeling on the window seat facing the glass, one finger drawing a line through the condensation, other hand flat against the window, seen from behind and slightly to the side, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, back three-quarter angle, waist-up framing, shot on Fujifilm Pro 400H, cool muted greens and fine grain, flat cool window light silhouetting her shoulders, faint warm rim from the lamp behind, sharp focus on the droplets, slightly underexposed, shadows crushed a little, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-03 — Селфи в приглушённом свете

*core · seed 106003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, handheld arm's-length selfie curled up in the window seat under the knitted throw, headphones pushed down around her neck, head resting on the cushion, soft tired smile into the lens, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 24mm front-facing phone camera look, slightly above eye level, natural selfie perspective, chest-up framing, shot on Fujifilm Pro 400H, cool muted greens and fine grain, soft grey window light on the face, warm lamp accent on the hair, visible low-light grain, one highlight blown out where the light hits hardest, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-04 — Ставит пластинку

*core · seed 106004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, kneeling in front of the low shelf lowering the needle onto a spinning vinyl record, hips settled back on her heels, back arched, glancing up at the camera through the loose strands, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, low camera near floor level, side three-quarter angle, full body framing, shot on Fujifilm Pro 400H, cool muted greens and fine grain, warm lamp key from camera left, cool grey window fill from the right, dark room between them, focus landing a touch behind the eyes, sharpest on the ear, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-05 — Портрет у окна, капли на стекле в расфокусе

*hero · seed 106005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, close portrait pressed close to the window glass, cheek near the surface, eyes lifted to the lens, loose strands sticking to the damp temple, lips slightly parted, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm portrait lens, eye level, tight head-and-shoulders framing, out-of-focus raindrops in the foreground, shot on Fujifilm Pro 400H, cool muted greens and fine grain, soft cold window key wrapping the face, deep shadow on the far cheek, catchlights shaped like the window, faint haze from a smudge on the front element, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-06 — Лежит на полу с книгой

*core · seed 106006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, lying on her stomach on the rug with ankles crossed and lifted behind her, propped up on both forearms, back arched, open book in front, chin lifted toward the camera with a slow look, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, high top-down angle from above, full body framing, shot on Fujifilm Pro 400H, cool muted greens and fine grain, even grey daylight from the window, warm candle pool near her head, soft shadowless falloff, slight motion blur in one hand from a slow shutter, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-07 — Стоит у окна, худи на плече

*core · seed 106007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, standing at the window with arms folded, weight on one hip, hoodie pulled off one shoulder exposing the tank strap, looking out at the rain in profile, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, side profile, thigh-up framing, shot on Fujifilm Pro 400H, cool muted greens and fine grain, strong cool window key from the front, dark room behind her, rain streaks projecting across her arm, subject a little off-centre with one shoulder cropped by the frame edge, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-08 — Деталь: наушники и цепочка

*filler · seed 106008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, cropped detail of her collarbones and neck with the white over-ear headphones resting around her neck and the silver star pendant hanging between them, chin cropped at the top of frame, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Fujifilm Pro 400H, cool muted greens and fine grain, soft cool side light picking out the skin texture and the brushed metal of the pendant, mild flare washing one corner of the frame, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-09 — Танцует одна под пластинку

*core · seed 106009*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, mid-motion barefoot spin in the middle of the room with headphones on, arms loose above her head, eyes closed, hair strands flying, lost in the music, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly low angle, full body framing with mild motion blur in the arms, shot on Fujifilm Pro 400H, cool muted greens and fine grain, cool daylight from the window with the warm lamp streaking through the movement, soft ambient shadows, grain heavier in the shadows where the exposure was pushed, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S06-10 — Общий план комнаты в дождь

*core · seed 106010*

```text
Sofia, 26-year-old woman, athletic hourglass figure, white over-ear headphones resting around her neck, cropped heather grey zip hoodie unzipped low over a white ribbed tank top, matching grey lounge shorts, thigh-high grey ribbed socks, thin silver chain with small star pendant, dark brown messy high bun with loose damp strands, minimal natural makeup, seen small from across the room sitting in the window niche with her back against the frame, knees up, mug beside her, dwarfed by the tall grey window, cozy sensual mood, cropped hoodie unzipped low over the fitted tank, bare thighs above the high socks, wistful smouldering look, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 24mm wide lens, eye level, wide environmental shot showing the whole room and the rain outside, shot on Fujifilm Pro 400H, cool muted greens and fine grain, big soft grey window light dominating the frame, warm lamp as a single accent, deep shadow in the foreground, colour a touch cool and uncorrected straight out of camera, quiet apartment on a rainy afternoon, large window covered in rain droplets and running streaks, blurred grey city beyond, deep window seat with cushions, knitted throw, white over-ear headphones, vinyl record player on a low shelf, stack of books, lit candle, cold grey daylight mixed with one warm lamp, condensation on the glass, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
