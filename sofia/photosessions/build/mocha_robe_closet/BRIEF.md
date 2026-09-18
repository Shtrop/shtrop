# Мокко и шёлковый халат (Mocha and Silk)

**ID сессии:** `S25` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 125000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Зеркальная гардеробная, тёплые лампы, бельё цвета мокко и длинный халат.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open
```

## Гардероб (единый для всех кадров)

`Y` — Кружевной комплект цвета мокко с подкладкой + длинный шёлковый халат.

```text
mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet
```

## Локация

Просторная гардеробная, зеркальные дверцы, тёплые лампы, бархатный пуф.

```text
spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S25-01 | Халат распахнут в зеркалах | hero | 35mm lens | — | 125001 |
| S25-02 | Сидя на пуфе, застёгивает ремешок | hero | 50mm lens | — | 125002 |
| S25-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 125003 |
| S25-04 | Отражение | core | 50mm lens | — | 125004 |
| S25-05 | Против света | core | 35mm lens | — | 125005 |
| S25-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 125006 |
| S25-07 | В рост, рука в волосах | core | 50mm lens | — | 125007 |
| S25-08 | Деталь | filler | 85mm lens | — | 125008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Kodak Portra 400, warm even grain
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S25-01 — Халат распахнут в зеркалах

*hero · seed 125001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet, standing between the mirrored wardrobe doors letting the long silk robe hang wide open over the mocha set, one hand on the door frame, hip pushed out, direct steady gaze, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, frontal with reflections on both sides, full body framing, shot on Kodak Portra 400, warm even grain, warm wardrobe lamps from above and the sides, soft even wrap, handheld frame tilted a degree or two off level, spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S25-02 — Сидя на пуфе, застёгивает ремешок

*hero · seed 125002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet, sitting on the velvet ottoman with one foot up on it, fastening the strap of a heel, back arched over the knee, robe slid off both shoulders, eyes lifted to the lens mid-motion, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, side three-quarter angle, full body framing, shot on Kodak Portra 400, warm even grain, warm lamp key from the side, soft falloff into the dark closet behind, slightly underexposed, shadows crushed a little, spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S25-03 — Прогиб, взгляд через плечо

*core · seed 125003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet, kneeling back on her heels on the velvet ottoman, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 400, warm even grain, warm strip lamps wrapping her from above, mirror reflections filling the shadow side, one highlight blown out where the light hits hardest, spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S25-04 — Отражение

*core · seed 125004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet, standing close to the mirrored wardrobe door, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Kodak Portra 400, warm even grain, warm strip lamps wrapping her from above, mirror reflections filling the shadow side, focus landing a touch behind the eyes, sharpest on the ear, spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S25-05 — Против света

*core · seed 125005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet, standing at the lit doorway of the closet with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Kodak Portra 400, warm even grain, warm strip lamps wrapping her from above, mirror reflections filling the shadow side, faint haze from a smudge on the front element, spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S25-06 — Полулёжа, нога вытянута

*core · seed 125006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet, reclining back on the velvet ottoman propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Kodak Portra 400, warm even grain, warm strip lamps wrapping her from above, mirror reflections filling the shadow side, slight motion blur in one hand from a slow shutter, spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S25-07 — В рост, рука в волосах

*core · seed 125007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet, standing tall between the two mirrored doors, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Kodak Portra 400, warm even grain, warm strip lamps wrapping her from above, mirror reflections filling the shadow side, subject a little off-centre with one shoulder cropped by the frame edge, spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S25-08 — Деталь

*filler · seed 125008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, mocha brown lace lingerie set with full opaque lining, soft cup bra and high-leg briefs, long ivory silk robe worn open and slipping off both shoulders, silver star pendant, hair pinned up with loose strands, bare feet, cropped detail composition of the lace edge of the bra under the open silk of the robe, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, mocha lace set under a long silk robe left hanging open, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Kodak Portra 400, warm even grain, warm strip lamps wrapping her from above, mirror reflections filling the shadow side, mild flare washing one corner of the frame, spacious walk-in closet, mirrored wardrobe doors on both sides, warm strip lamps, velvet ottoman, rows of hanging clothes in muted tones, shoe shelves, soft carpet, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
