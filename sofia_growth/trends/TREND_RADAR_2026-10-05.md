# Trend Radar — 5 октября 2026

**Метка:** `AI ANALYSIS` — открытые публикации о платформе, не метрики аккаунта Sofia.
Предыдущий радар: [2026-09-28](TREND_RADAR_2026-09-28.md).

**Оговорка по источникам.** Прямое чтение страниц из этой сессии закрыто сетевой политикой
окружения: проверялись выдачи веб-поиска, а не сами страницы. Цифры из вторичных обзоров
помечены `confidence: low`, расхождения оставлены расхождениями.

---

## Главное за неделю: правила те же, формулировки жёстче

За 29 сентября — 5 октября платформа не объявила ни одного нового ранжирующего сигнала.
Продуктовые анонсы недели (29.09: общая доступность Live-видеорекламы, AI-агент Muse для
малого бизнеса, школьная программа Meta) к выпуску Sofia отношения не имеют.

Что действительно уточнилось — вес пересылок. Октябрьские обзоры приводят формулировку
Mosseri резче прежней: **пересылка — сильнейший сигнал, который у платформы вообще есть**,
сильнее watch time, сохранений и вовлечения, потому что это адресная рекомендация
конкретному неподписчику. И его же уточнение по тройке сигналов: лайки чуть важнее для
**connected** контента (свои подписчики), пересылки — для **unconnected** (неподписчики).
Для цели «растить подписчиков» это значит ровно одно: считать sends, а не лайки.

## Что уточнилось в ранжировании

| Сигнал | Было (28.09) | Стало (05.10) |
|---|---|---|
| Sends per reach | сильнейший сигнал нефолловерского охвата | сильнейший сигнал платформы **вообще**, в формулировке Mosseri |
| Likes per reach | слабейший из трёх | слабейший, с разделением: лайки — для подписчиков, sends — для неподписчиков |
| Длина Reels | расхождение 45-60 с против 7-15 с | добавилось третье утверждение: ролики **длиннее 3 минут** перестают подаваться неподписчикам — причём тот же обзор рядом пишет обратное. Расхождение не снято; практическое правило: за 3 минуты не заходить |
| Монтаж | хук в первом кадре | добавлена норма темпа: склейка каждые 3-5 с (оценка «+72% к шансу вирусного разноса» — один вторичный источник, `confidence: low`) |

## Новые форматы в бэклоге

- **Loading-процент (0% → 100%).** Счётчик держит зрителя до конца и петля стыкуется сама
  собой — прямая работа на долю досмотров. Для студии это раскадровка из уже существующих
  рендеров, без новых моделей. Вошёл в бэклог шестым.
- **Процесс целиком.** Детальный процесс набирает долгое удержание, выходя за рамки короткого
  ролика. Для Sofia это канон персоны буквально: капучино как процесс, а не как реквизит.
  Риск назван: процесс без хука в первом кадре умирает на skip rate, поэтому начинать
  с результата и только потом разворачивать путь к нему.

Под оба формата хуки дописаны вручную в `data/hook_bank.json` — генератор их не сочиняет.

## Уточнение по аудио

Правило было «своё аудио вместо трендового». Октябрьские обзоры смещают акцент: решает не
происхождение трека, а **соответствие аудио жанру кадра** — речь под сценку, узнаваемый трек
под переход, сдержанная музыка под уязвимость, энергичный — под монтаж-трансформацию.
Для студии с XTTS это упрощение: своя речь и так лучший вариант для сценок и storytime.

## Что не изменилось

Метка `AI-generated profile` остаётся условием попадания в рекомендации: публикации
нераскрытого AI-профиля не показываются в Reels и Explore тем, кто не подписан. Раскрытый
профиль охвата не теряет и штрафа за AI-природу не несёт. Stories по-прежнему без
нефолловерского охвата, оригинальность по-прежнему до 3x, малым аккаунтам платформа
по-прежнему подталкивает охват.

## Изменения в данных

- `data/trend_radar.json`: `radar_date` → 2026-10-05. Добавлено правило `prod-jump-cut-cadence`,
  сигнал аудитории `aud-reels-engagement-up` (вовлечение Reels +~24.8% год к году,
  `confidence: low`), два формата — `fmt-loading-percentage`, `fmt-process-long-watch`.
  Уточнены `rank-sends-per-reach`, `rank-likes-per-reach-weakest`, `rank-longer-reels-reach`
  (остаётся `CONFLICTING`), `fmt-original-audio`.
- `data/hook_bank.json`: 27 хуков на 11 форматов (было 20 на 9). Банк углублён сознательно:
  прокрутка хуков в генераторе плана работает только там, где есть из чего выбирать.
- `tools/trend_radar.py`: рычаги для двух новых форматов заданы явно, а не дефолтом.
- `tools/plan_builder.py`: план больше не повторяется неделя за неделей — хуки и
  эксперименты прокручиваются по истории прежних планов (см. комментарий к PR).

## Источники

- [Instagram Reel Trends 2026: форматы и идеи, которые дают охват — Vaizle](https://insights.vaizle.com/instagram-reel-trends/)
- [Instagram Trends: October 2026 — New Engen](https://newengen.com/insights/instagram-trends/)
- [10 Instagram Trends Backed By Real Data in 2026 — Metricool](https://metricool.com/instagram-trends/)
- [Adam Mosseri on Shares: The Real Instagram Signal in 2026 — Socialync](https://www.socialync.io/blog/adam-mosseri-shares-instagram-algorithm-2026)
- [Mosseri Restates the Signals That Decide Reach — Kompozy](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance)
- [Instagram algorithm 2026: updates and tips — Gyre](https://gyre.pro/blog/instagram-algorithm-updates-and-tips-to-boost-your-visibility)
- [Instagram AI-Generated Profile Labels 2026: Reach Rules — Truescho](https://truescho.com/en/blog/instagram-ai-generated-profile-labels-2026)
- [Instagram will limit reach for AI influencers who skip the label — Digital Trends](https://www.digitaltrends.com/social-media/instagram-will-limit-reach-for-ai-influencers-who-skip-ai-generated-label-on-their-profile/)
- [September 2026 Social Media News for Creators — Stack Influence](https://stackinfluence.com/blog/september-2026-social-media-news-and-updates-for-creators)
- [The social media updates to know in October 2026 — Brandnation](https://brandnation.co.uk/news-insights/the-social-media-updates-to-know-in-october-2026)
