# Trend Radar — 21 сентября 2026

**Метка:** `AI ANALYSIS` — открытые публикации о платформе, не метрики аккаунта Sofia.
Предыдущий радар: [2026-09-15](TREND_RADAR_2026-09-15.md).

---

## Главное за неделю: раскрытие AI стало вопросом охвата

**Meta объявила 31 августа 2026:** аккаунты, построенные вокруг AI-персоны **без раскрытия**,
получают пониженную дистрибуцию в рекомендациях — включая Reels и Explore. Метка
«AI creator» заменена на явную **«AI-generated profile»**.

Корректно раскрытый AI-профиль **сохраняет обычный охват**: штрафа за синтетическую
личность как таковую нет.

Неделю назад это было стратегической рекомендацией («раскрытие даёт премию доверия»).
Теперь это политика платформы с прямым влиянием на дистрибуцию.

**Что проверить у Sofia в первую очередь:** стоит ли на аккаунте метка AI-generated profile.
Если нет — это кандидат в причины охвата 49 на публикацию, наравне с тем, что публикуются
почти одни Stories. Проверяется в настройках профиля и не требует ни рендера, ни GPU.

## Что уточнилось в ранжировании

| Сигнал | Было (15.09) | Стало (21.09) |
|---|---|---|
| Оригинальность | +40-60% дистрибуции | **до 3x**; водяные знаки TikTok и переработка старого понижаются |
| Watch time | Сумма секунд с повторами | **Доля досмотров** — главная метрика Reels |
| Saves | Заметно ниже sends | **Наравне с shares**; лайки — слабейший сигнал |
| Размер аккаунта | — | Платформа **подталкивает малые аккаунты**: низкий охват объясняется контентом и поверхностью, а не размером |

Последнее важно для Sofia: отговорка «мало подписчиков, поэтому нет охвата» не работает.

## Новые форматы в бэклоге

- **Эпизодические серии вместо разовых трендов.** Зритель возвращается за продолжением;
  досматриваемость и возвраты выше, чем у одиночных роликов.
- **Оригинальное аудио вместо трендовых треков.** Сигнализирует алгоритму о свежем контенте
  и не попадает под понижение за переиспользование. Для студии с XTTS — дешёвый ход.

Под оба добавлены хуки в `data/hook_bank.json`.

## Что не изменилось

Sends per reach остаётся сильнейшим сигналом нефолловерского охвата, skip rate по-прежнему
ранжирующий, audition на неподписчиках работает. Формат первого кадра — текст + движение +
лицо — актуален; текстовые оверлеи отдельно отмечены как обязательные, потому что большинство
смотрит без звука.

## Источники

- [Instagram Limits Reach for Undisclosed AI Profiles — Affiverse](https://www.affiversemedia.com/instagram-undisclosed-ai-profile-reach-limits/)
- [Instagram to label AI-generated profiles, limit reach — American Bazaar](https://americanbazaaronline.com/2026/09/01/instagram-to-label-ai-generated-profiles-487368/)
- [Instagram ties AI disclosure to reach — BuzzInContent](https://www.buzzincontent.com/insight/instagram-ties-ai-disclosure-to-reach-raising-stakes-for-virtual-influencers-and-brands-12486926)
- [Instagram Algorithm Update 2026: New Ranking Factors](https://leeseohits.com/blog/industry-news/instagram-algorithm-update-2026-new-ranking-factors)
- [Instagram Algorithm Changes in 2026 — Heropost](https://heropost.io/instagram-algorithm-changes-2026/)
- [How the Instagram Algorithm Works: 2026 Guide — Buffer](https://buffer.com/resources/instagram-algorithms/)
- [The Instagram Reels Algorithm in 2026 — Fastlane](https://www.usefastlane.ai/blog/instagram-reels-algorithm-2026)
- [The 2026 Instagram Trends Creators Are Actually Doing — Manychat](https://manychat.com/blog/instagram-trends-for-creators-2026/)
- [Reel Trends 2026 — The Social Content Factory](https://thesocialcontentfactory.com/reel-trends)
