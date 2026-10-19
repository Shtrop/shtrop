# Trend Radar — 28 сентября 2026

**Метка:** `AI ANALYSIS` — открытые публикации о платформе, не метрики аккаунта Sofia.
Предыдущий радар: [2026-09-21](TREND_RADAR_2026-09-21.md).

**Оговорка по источникам.** Из этой сессии прямое чтение страниц закрыто сетевой политикой
окружения: проверялись выдачи веб-поиска, а не сами страницы. Поэтому цифры из вторичных
обзоров помечены `confidence: low/medium`, а расхождения между обзорами оставлены
расхождениями, а не усреднены.

---

## Главное за неделю: новых правил ранжирования не появилось — появилась цена уже известных

За 22-28 сентября ни Meta, ни Mosseri не объявили нового ранжирующего сигнала. Зато
уточнилось, сколько стоит то, что уже известно, и здесь неделя дала самый жёсткий вывод
за всё время работы радара.

**Stories не дают нефолловерского охвата вообще.** Не «меньше» — вообще: поверхность
адресована тем, кто уже подписан. Типовой охват Stories — 2-9% от подписчиков против
13-27% у постов; выход на неподписчиков у этой поверхности отсутствует по устройству.
Ежедневные Stories поднимают охват до ~11.4%, Stories вместе с Reels в тот же день —
до ~22.8%. То есть Stories усиливают Reels, но не заменяют их.

**Что это значит для Sofia напрямую.** 53 из 70 фактических публикаций — Stories, ещё
17 — одиночные фото, а одиночное фото по охвату слабейший формат (Reels ~2.25x к нему,
карусель ~3x). Значит охват 49 на публикацию — не загадка и не следствие размера аккаунта:
большая часть выпуска физически не могла принести новых подписчиков, а меньшая шла
слабейшим форматом. Reels, post и carousel не опубликованы ни разу.

**Цена нулевого блокера тоже уточнилась.** Сентябрьские обзоры формулируют последствие
отсутствия метки `AI-generated profile` резче, чем формулировка от 31 августа: публикации
нераскрытого AI-профиля не показываются в Reels и Explore тем, кто ещё не подписан.
Нефолловерский охват — единственный канал новых подписчиков; без метки он обнуляется
вне зависимости от качества контента.

## Что уточнилось в ранжировании

| Сигнал | Было (21.09) | Стало (28.09) |
|---|---|---|
| Тройка сигналов | watch time, sends per reach | добавлен третий — **likes per reach**, слабейший из трёх: лайки работают на охват среди подписчиков, пересылки — среди неподписчиков |
| Длина Reels | «до 3 минут попадают в рекомендации», confidence low | **расхождение зафиксировано**: часть обзоров даёт пик на 45-60 с, часть — на 7-15 с. Не усреднено. Рабочее правило: оптимизировать долю досмотров, а не длину |
| Skip rate | ранжирующий сигнал | добавлен порог: hold rate >60% на 3-й секунде против <40% — разница в охвате в 5-10 раз по оценке одного обзора (`confidence: low`, Meta не подтверждала) |
| Карусель | сохраняемый формат | при высоком swipe-through платформа **переподаёт карусель через 24-48 часов** тем, кто не пролистал — второй шанс, которого нет ни у одного другого формата |
| Поверхности | Reels / Feed / Stories | добавлена **Stories без нефолловерского охвата** как отдельное правило: поверхность решает раньше, чем контент |

## Новое в продукте платформы — и что из этого нам не нужно

- **Репост чужих Reels и постов** (обновление сентября): лайки, просмотры и комментарии идут
  в статистику **оригинала**, репост живёт в отдельной вкладке `Reposted` и не попадает в сетку.
  В план роста не закладывается: своей дистрибуции не строит, а под штраф за неоригинальность
  попасть можно.
- **Series** (тест с 2 июня 2026): серия получает свою страницу, вкладку в профиле и кнопку
  Watch Next. Тест ограничен отобранными авторами — рассчитывать на доступ нельзя, но
  эпизодический формат работает и без функции, он уже в бэклоге.
- **Instagram for TV** (Fire TV с декабря 2025, Google TV с февраля 2026): Reels крутятся
  каналами, автоматически и со звуком, на большом экране. Новостью недели это не является,
  но в радаре не было, а вывод прикладной: рендер 480×832 на телевизоре выглядит браком,
  тогда как на телефоне ещё проходил. Подкрепляет блокер 1.
- **First Draft** (автоматическая черновая нарезка Reels, iPhone, с конца августа): проверено
  и отклонено — студия рендерит по своему пайплайну, ручная нарезка в приложении не наш путь.
- **«Your Algorithm»** (декабрь 2025 → июнь 2026 на Feed, Reels, Explore): пользователь сам
  задаёт интересы. На выпуск не влияет; отмечено, чтобы не принять за новость.

## Что не изменилось

Sends per reach остаётся сильнейшим сигналом нефолловерского охвата, saves идут наравне
с shares, оригинальность даёт до 3x дистрибуции, audition на неподписчиках работает,
малым аккаунтам платформа подталкивает охват — отговорка «мало подписчиков» по-прежнему
не работает.

## Изменения в данных

- `data/trend_radar.json`: `radar_date` → 2026-09-28. Добавлено 6 правил платформы
  (`rank-likes-per-reach-weakest`, `surface-stories-no-discovery`, `surface-format-reach-ratio`,
  `rank-3sec-hold-rate`, `rank-repost-credits-original`, `surface-tv-quality-bar`).
  Уточнены `rank-longer-reels-reach` (помечен `status: CONFLICTING`), `fmt-episodic-series`,
  `fmt-saveable-carousel`, `aud-ai-profile-label-policy`.
- `data/hook_bank.json`: новых форматов за неделю не появилось, поэтому новые форматы
  не заводились. Дописаны хуки к трём самым тонким форматам бэклога
  (`fmt-this-or-that`, `fmt-storytime-direct-to-camera`, `fmt-transition-sketch-to-reality`) —
  было по одному, стало по два. Итого 20 хуков на 9 форматов.

Сигнал про телевизор сознательно лежит в `platform_rules`, а не в `format_signals`: это
планка производства, а не контентный формат, и в бэклоге экспериментов ему делать нечего.

## Источники

- [Instagram puts new limits on undisclosed AI profiles — TechCrunch, 31.08.2026](https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/)
- [Instagram AI-Generated Profile Labels 2026: Reach Rules — Truescho](https://truescho.com/en/blog/instagram-ai-generated-profile-labels-2026)
- [Instagram algorithm tips for 2026 — Hootsuite](https://blog.hootsuite.com/instagram-algorithm/)
- [Instagram Stories 2026: completion rates, views, engagement benchmarks — Upgrow](https://www.upgrow.com/blog/instagram-stories-2026-completion-rates-views-engagement-benchmarks)
- [Reels vs Carousels vs Images: data study 2026 — Collabkit](https://collabkit.me/blog/instagram-reels-vs-carousels-vs-images-data-study-2026)
- [2026 Instagram Organic Engagement Benchmarks — Socialinsider](https://www.socialinsider.io/social-media-benchmarks/instagram)
- [Instagram Carousel Statistics 2026 — Notes2Pic](https://www.notes2pic.com/blog/instagram-carousel-statistics)
- [Instagram Algorithm 2026: Watch Time and Sends per Reach — Blck Alpaca](https://blckalpaca.at/en/knowledge-base/social-media/social-media-algorithms-distribution/instagram-algorithm-2026)
- [Best Instagram Reel Length in 2026 (Data-Backed) — Moonb](https://www.moonb.io/blog/instagram-reel-length)
- [Instagram Reels Reach 2026 — TrueFuture Media](https://www.truefuturemedia.com/articles/instagram-reels-reach-2026-business-growth-guide)
- [Instagram now lets you repost grid posts and Reels — NewsBytes](https://www.newsbytesapp.com/news/science/instagram-now-lets-you-repost-grid-posts-and-reels/tldr)
- [Instagram 'Series' is the latest feature to launch on the app — RUSSH](https://www.russh.com/what-is-instagram-series/)
- [Introducing Instagram for TV — About Instagram](https://about.instagram.com/blog/announcements/instagram-tv-app)
- [Instagram's 'First Draft' feature aims to make editing Reels less tedious — TechCrunch, 25.08.2026](https://techcrunch.com/2026/08/25/instagrams-first-draft-feature-aims-to-make-editing-reels-less-tedious/)
- [Instagram Rolls Out Algorithm Control Option to All English-Speaking Users — Social Media Today](https://www.socialmediatoday.com/news/instagram-rolls-out-algorithm-control-option-to-all-english-speaking-users/809524/)
