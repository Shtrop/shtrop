# Корсет при свечах (Corset by Candlelight)

**ID сессии:** `S28` · **Кадров:** 8 · **Формат:** 4:5 · **Base seed:** 128000

**Референс:** Бельевая линия — максимальный гламурный регистр, 8 кадров, без наушников

**Настроение:** Кирпичный погреб, десятки свечей, корсет с подвязками. Самый тёмный и плотный свет.

**Подача (слой на каждом кадре):**

```text
lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin
```

## Гардероб (единый для всех кадров)

`AB` — Корсет со шнуровкой + подвязки и чулки, плотная ткань.

```text
black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet
```

## Локация

Кирпичный погреб, дубовые бочки, только свечи как источник света.

```text
brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source
```

## Раскадровка

| # | Кадр | Тип | Оптика / ракурс | Наушники | Seed |
|---|------|-----|-----------------|----------|------|
| S28-01 | Затягивает шнуровку | hero | 50mm lens | — | 128001 |
| S28-02 | На дубовой бочке | hero | 35mm lens | — | 128002 |
| S28-03 | Прогиб, взгляд через плечо | core | 35mm lens | — | 128003 |
| S28-04 | Отражение | core | 50mm lens | — | 128004 |
| S28-05 | Против света | core | 35mm lens | — | 128005 |
| S28-06 | Полулёжа, нога вытянута | core | 35mm lens | — | 128006 |
| S28-07 | В рост, рука в волосах | core | 50mm lens | — | 128007 |
| S28-08 | Деталь | filler | 85mm lens | — | 128008 |

Наушники на шее: 0/8 кадров (канон-ориентир — 70% по всему дню, не по одной сессии).

## Технический прогон

- Pipeline: ComfyUI + FLUX + Sofia LoRA/PuLID
- Разрешение: 896x1152, апскейл 1.5x latent + face detailer pass
- Steps 30, guidance 3.5, sampler `TODO_FROM_STUDIO_WORKFLOW`
- Плёнка сессии: shot on Cinestill 800T pushed one stop, heavy grain and candle halation
- Против пластика см. `REALISM.md`: guidance, вес LoRA, face detailer, зерно
- LoRA `TODO_FROM_PERSONA_CONFIG`, PuLID `TODO_FROM_PERSONA_CONFIG` — подставить из persona config
- Seed: per-session base seed, +1 per shot; hero shots get 4 seed variants; по 4 варианта на кадр
- GPU: RTX 5090 32GB — один GPU job за раз, проверять gpu_resource_scheduler

## Промпты по кадрам

### S28-01 — Затягивает шнуровку

*hero · seed 128001*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet, standing among the candles with her back half to the camera, both hands pulling the corset laces tight behind her, shoulder blades drawn together, head turned to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, back three-quarter angle, thigh-up framing, shot on Cinestill 800T pushed one stop, heavy grain and candle halation, dozens of candle flames from below and the side, deep black brick behind, handheld frame tilted a degree or two off level, brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S28-02 — На дубовой бочке

*hero · seed 128002*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet, sitting on the old oak barrel with one heel up on its rim, elbow on that knee, the other leg long to the floor, garter strap taut, slow heavy-lidded look at the camera, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera, three-quarter front, full body framing, shot on Cinestill 800T pushed one stop, heavy grain and candle halation, candlelight pooling warm on her legs and chest, everything beyond falling to black, slightly underexposed, shadows crushed a little, brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S28-03 — Прогиб, взгляд через плечо

*core · seed 128003*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet, kneeling back on her heels on the flat top of the oak barrel, spine deeply arched, one hand planted beside her, head turned over the shoulder holding direct eye contact with the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, slightly above eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T pushed one stop, heavy grain and candle halation, dozens of candle flames from below, flickering warm, one cooler shaft from the cellar archway behind her, one highlight blown out where the light hits hardest, brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S28-04 — Отражение

*core · seed 128004*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet, standing close to a dark sheet of glass leaning against the brick, one hand flat on the surface, hip pushed out, chin lowered, meeting the camera past her own reflection, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, eye level, over-the-shoulder into the reflection, thigh-up framing, shot on Cinestill 800T pushed one stop, heavy grain and candle halation, dozens of candle flames from below, flickering warm, one cooler shaft from the cellar archway behind her, focus landing a touch behind the eyes, sharpest on the ear, brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S28-05 — Против света

*core · seed 128005*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet, standing at the narrow cellar archway with light beyond with one forearm raised against the frame, weight settled on one hip, the long line of her back and legs read against the light, head turned just enough to find the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, eye level, back three-quarter angle, full body vertical framing, shot on Cinestill 800T pushed one stop, heavy grain and candle halation, dozens of candle flames from below, flickering warm, one cooler shaft from the cellar archway behind her, faint haze from a smudge on the front element, brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S28-06 — Полулёжа, нога вытянута

*core · seed 128006*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet, reclining back on the flat top of the oak barrel propped on both elbows, one knee raised and the other leg stretched long, ribcage lifted, chin up, half-lidded gaze straight down the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 35mm lens, low camera at surface level, three-quarter front angle, full body framing, shot on Cinestill 800T pushed one stop, heavy grain and candle halation, dozens of candle flames from below, flickering warm, one cooler shaft from the cellar archway behind her, slight motion blur in one hand from a slow shutter, brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S28-07 — В рост, рука в волосах

*core · seed 128007*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet, standing tall among the candles on the stone floor, one hand pushing back through her hair with the elbow raised, weight on one leg so the hip breaks the line, chin down and eyes up into the lens, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 50mm lens, slightly low angle, frontal, full body framing, shot on Cinestill 800T pushed one stop, heavy grain and candle halation, dozens of candle flames from below, flickering warm, one cooler shaft from the cellar archway behind her, subject a little off-centre with one shoulder cropped by the frame edge, brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```

### S28-08 — Деталь

*filler · seed 128008*

```text
Sofia, 26-year-old woman, athletic hourglass figure, black laced corset with structured boning and full opaque lining, matching garter belt with straps clipped to sheer black stockings, high-cut briefs, silver star pendant, hair loose and falling forward, bare feet, cropped detail composition of the garter strap clipped to the stocking top and the corset lacing at her waist, face out of frame, fingers relaxed and naturally posed, lingerie editorial glamour at its boldest, set with full opaque lining, deep neckline and high-cut briefs, sculpted waist and long legs fully on show, unhurried commanding sensuality, direct gaze, laced corset with garter straps and stockings, candle flame on bare skin, real human skin with visible pores and fine peach fuzz, small blemishes and uneven tone left unretouched, faint redness at the knuckles, elbows and knees, shine only where skin is really oily, fine creases at the wrists and the inside of the elbow, a few stray hairs out of place, makeup that reads as applied by hand rather than airbrushed, the proportions of a real athletic woman, 85mm lens, close detail framing, very shallow depth of field, shot on Cinestill 800T pushed one stop, heavy grain and candle halation, dozens of candle flames from below, flickering warm, one cooler shaft from the cellar archway behind her, mild flare washing one corner of the frame, brick vaulted wine cellar, rows of dusty bottles, old oak barrels, dozens of lit candles on the stone floor and ledges, cobwebs in the corners, no other light source, suggestive glamour editorial, sensual magazine styling, body-conscious flattering framing, confident alluring presence, candid unretouched photograph, shot on a full-frame camera with a fast prime lens wide open, available light only, true-to-life muted colour, slight lens vignetting, mild chromatic aberration towards the edges, fine film grain, imperfect focus falloff, natural motion in the hands and hair
```
