# Trend Radar — 19 октября 2026

**Метка:** `AI ANALYSIS` — открытые публикации о платформе, не метрики аккаунта Sofia.
Предыдущий радар: [2026-10-12](TREND_RADAR_2026-10-12.md).

**Оговорка по источникам.** Прямое чтение страниц из этой сессии закрыто сетевой политикой
окружения: проверялись выдачи веб-поиска, а не сами страницы.

---

## Главное за неделю: нашлись два обхода блокера рендера

Новых правил ранжирования платформа не объявила. Зато нашлись две механики, которые дают
нефолловерский охват **не дожидаясь** Reels в 1080×1920 — а именно этот блокер держит рост
с самого начала.

### 1. Карусель с музыкой попадает в Reels-таб

Фотокарусель с добавленным треком становится **допустимой** для Reels-таба, то есть для
поверхности, адресованной неподписчикам. По одному из разборов — с октября 2024.
Допустимость не равна дистрибуции, и описание механики найдено только во вторичных блогах:
публикации платформы под это не нашлось, поэтому `confidence: low`.

Почему это важно именно сейчас: фото-пайплайн студии работает, карусели уже в плане,
добавить нужно только трек. Это единственный известный путь к нефолловерской поверхности,
пока рендер Reels упирается в блокер 1. Сравнения охвата карусели и Reels расходятся
(Reels впереди примерно на треть в одном разборе, карусели впереди по вовлечению в другом),
так что выбирать формат по обзорам смысла нет — только по своему замеру.

### 2. Trial Reels — готовый инструмент замера, которого не хватало контуру

Trial Reel уходит на 24-72 часа **только неподписчикам**: в профиле и в ленте подписчиков
его нет, статистика приходит примерно через сутки, с весны 2026 его можно планировать
заранее. Порог по подписчикам источники называют по-разному: свежие пересказы Help Center
говорят про 200 для профессионального (creator/business) аккаунта и 1000 для личного, часть
гайдов повторяет 1000 для всех — проверять в самом Help Center.

Это ровно то, чего не хватало: честный замер нефолловерского охвата без публикации в сетку,
то есть первые REAL-числа для KPI, которые сейчас все `NOT_MEASURED`.

**Важная связка:** аккаунт, не допущенный до рекомендаций, теряет и доступ к Trial Reels.
То есть нулевой блокер — метка `AI-generated profile` — закрывает не только охват, но и
сам инструмент измерения. Порядок действий от этого не меняется, а становится жёстче:
сначала метка, потом всё остальное.

## Что уточнилось

| Сигнал | Стало (19.10) |
|---|---|
| Оригинальность | по сообщению MediaPost, около 75% рекомендаций в США приходится на публикации, которые алгоритм считает оригинальными. Цифра из отчёта, не из публикации платформы, но порядок величины говорит: оригинальность — условие попадания в рекомендации, а не бонус |
| AI-перевод Reels | подтверждается вторым источником: добавлены японский, корейский, французский, немецкий, итальянский |
| «Your Algorithm» | по странице платформы функция уже на всех поверхностях (Feed, Reels, Explore). На выпуск не влияет, отмечено чтобы не принять за новость |

## Что это меняет в бэклоге

`fmt-carousel-with-music` добавлен в бэклог и сразу получил слот эксперимента в плане на
20-30.10 — прокрутка, сделанная 05.10, отдаёт слот ни разу не пробованному формату раньше
старых гипотез. Под формат дописаны два хука вручную: 29 хуков на 12 форматов.

По score формат стоит низко: `confidence: low` придавливает его вниз, потому что ранжирование
не знает про блокер рендера. Это ограничение модели названо прямо — приоритет здесь задаёт
не score, а то, что остальные форматы требуют Reels, которых нет.

## Изменения в данных и коде

- `data/trend_radar.json`: `radar_date` → 2026-10-19. Добавлены `surface-trial-reels` и
  `fmt-carousel-with-music`, уточнён `rank-originality-penalty`.
- `data/hook_bank.json`: 29 хуков на 12 форматов.
- `tools/trend_radar.py`: рычаги нового формата заданы явно.
- `tools/plan_builder.py`: слот подписывается по носителю формата, а не по позиции в неделе —
  карусель в экспериментальном слоте больше не называется Reel. Подписать карусель как Reel
  значит врать в плане, по которому работает студия.

## Источники

- [The One Instagram Setting That Gets Your Carousel Into the Reels Feed — Dustin Hill](https://dustinhill.com.sg/blog/instagram-carousel-music-reels-feed/)
- [Instagram Carousel Posts: Templates, Sizes & 12 Tips — CreatorFlow](https://creatorflow.so/blog/instagram-carousel-posts-guide/)
- [Instagram Carousel Posts vs Reels: 2026 Performance Data — Wavevision](https://www.wavevision.io/blog/instagram-carousel-posts-vs-reels-performance-comparison-2026-data)
- [Carousels vs Reels on Instagram: what the 2026 data says — Showfolk](https://www.showfolk.ai/blog/instagram-carousels-vs-reels-reach)
- [Instagram allows creators to schedule Trial Reels — Social Media Today](https://www.socialmediatoday.com/news/instagram-allows-creators-to-schedule-trial-reels/816549/)
- [How to Use Instagram Trial Reels to Grow Your Account — CreatorFlow](https://creatorflow.so/blog/instagram-trial-reels/)
- [Instagram Trial Reels: Test on Non-Followers — Exemplary](https://exemplary.ai/blog/instagram-trial-reels)
- [Instagram Algorithm Update Discourages Reposted Content — MediaPost](https://www.mediapost.com/publications/article/414773/instagram-algorithm-update-discourages-reposted-co.html)
- [Control Your Instagram Reels Algorithm — About Instagram](https://about.instagram.com/blog/announcements/reels-algorithm-control)
- [Instagram Updates & News 2026 — Metricool](https://metricool.com/instagram-news/)
