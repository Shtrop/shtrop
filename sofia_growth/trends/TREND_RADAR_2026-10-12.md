# Trend Radar — 12 октября 2026

**Метка:** `AI ANALYSIS` — открытые публикации о платформе, не метрики аккаунта Sofia.
Предыдущий радар: [2026-10-05](TREND_RADAR_2026-10-05.md).

**Оговорка по источникам.** Прямое чтение страниц из этой сессии закрыто сетевой политикой
окружения: проверялись выдачи веб-поиска, а не сами страницы.

---

## Главное за неделю: радар исправляет собственную цифру

Новых правил ранжирования платформа за 6-12 октября не объявила. Зато проверка источников
нашла ошибку в самом радаре, и она жила в нём почти месяц.

**«Sends весят ~3-5x лайка» — цифра без первоисточника.** Этот радар нёс её с 15 сентября
как `confidence: high`, playbook ставил её в первый пункт приоритета рычагов. Проверка
показала: числового веса сигналов платформа никогда не публиковала, множитель встречается
только во вторичных блогах (часть из них ссылается друг на друга), а сам Mosseri сказал
про пересылки «**slightly** more important» для unconnected контента и «один из крупнейших
сигналов ранжирования».

Что осталось в силе:

- пересылка — главный рычаг охвата у неподписчиков, потому что это адресная рекомендация
  конкретному человеку;
- разделение Mosseri: лайки чуть важнее для connected контента (свои подписчики),
  пересылки — для unconnected;
- для цели «растить подписчиков» KPI остаётся sends per reach.

Что снято:

- множитель 3-5x — помечен `FIGURE_RETRACTED` с полем `retracted_claim`;
- «лайки — слабейший сигнал, не оптимизировать» переформулировано: это вывод обзоров,
  а разница у платформы названа словом «slightly»;
- пороги 1-2% и >3% shares/reach остались ориентирами **вторичных** обзоров — держим как
  гипотезу до собственного замера, не как норматив.

Поправка проставлена и в архивном радаре 15.09, чтобы цифру оттуда не прочли как текущую.

## Что уточнилось по правилам

| Сигнал | Было | Стало (12.10) |
|---|---|---|
| Sends per reach | «вес ~3-5x лайка», high | `FIGURE_RETRACTED`, medium: направление подтверждено словами Mosseri, множитель снят |
| Оригинальность | «до 3x дистрибуции» для Reels | с конца апреля 2026 правило охватывает **фото и карусели**; аккаунт, публикующий в основном не своё, теряет рекомендации неподписчикам (подписчики пост видят). Рамка, водяной знак, субтитры и кредит оригинальность не создают. Право восстанавливается, если большинство публикаций за скользящие 30 дней оригинальны. Множитель «до 3x» — тоже оценка обзоров |
| Длина Reels | расхождение 45-60 с против 7-15 с, плюс потолок 3 минуты | расхождение уже четвёртое: добавилось «Reels теперь до 20 минут». Не усредняем. Правило то же: решает доля досмотров, за 3 минуты не заходить без своего замера |
| Метка AI-профиля | без метки нет рекомендаций неподписчикам | добавилось: при ошибочной пометке есть апелляция, но по сообщениям она занимает **недели**. Ещё один довод поставить метку самому. Раскрытый профиль охвата не теряет, виртуальные инфлюенсеры не под запретом |

## Новое: AI-перевод Reels с подгонкой артикуляции

Перевод Reels расширили языками (сообщают о японском, корейском, французском, немецком,
итальянском), и он правит движения губ под переведённую речь. Для Sofia это дешёвый выход
за пределы русскоязычной аудитории: голос и так синтезируется, артикуляцию правит сама
платформа. Сообщения вторичные, дата рассылки первоисточником не подтверждена, поэтому
`confidence: low` — проверять наличие функции в аккаунте, а не планировать на неё.

## Что не изменилось

Stories без нефолловерского охвата, порядок форматов по охвату (Reels > карусель >
одиночное фото), норма темпа монтажа 3-5 с, малым аккаунтам платформа подталкивает охват.
Бэклог форматов не менялся: новых форматов за неделю не появилось, новые хуки не заводились.

## Изменения в данных

- `data/trend_radar.json`: `radar_date` → 2026-10-12. `rank-sends-per-reach` помечен
  `FIGURE_RETRACTED` и понижен до medium, переформулированы `rank-likes-per-reach-weakest`,
  `rank-originality-penalty`, `rank-longer-reels-reach`, `aud-ai-profile-label-policy`.
  Добавлено правило `surface-reels-ai-translation`.
- `strategy/GROWTH_PLAYBOOK.md`: версия 12.10, множитель снят в приоритете рычагов,
  оригинальность описана по фактическому охвату правила.
- `trends/TREND_RADAR_2026-09-15.md`: поправка в начале файла.
- `data/hook_bank.json` не менялся: 27 хуков на 11 форматов.

## Источники

- [Instagram Shares Algorithm Insights To Inform Strategy — Social Media Today](https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/)
- [Mosseri Restates the Signals That Decide Reach — Kompozy](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance)
- [Instagram Chief Confirms Sends Drive Algorithm Rankings — SMK](https://smk.co/instagram-chief-confirms-sends-drive-algorithm-rankings/)
- [Instagram Algorithm 2026: 5 Ranking Signals Mosseri Confirmed — Dataslayer](https://www.dataslayer.ai/blog/instagram-algorithm-2025-complete-guide-for-marketers)
- [Instagram expands original content policy to photos and carousels — Social Samosa](https://www.socialsamosa.com/news-2/instagram-original-content-policy-11801189)
- [Instagram Algorithm Update Discourages Reposted Content — MediaPost](https://www.mediapost.com/publications/article/414773/instagram-algorithm-update-discourages-reposted-co.html)
- [Instagram ties AI profile labels to reach — ContentGrip](https://www.contentgrip.com/instagram-ai-profile-labels/)
- [Instagram cracking down on accounts featuring AI-generated influencers — 9to5Google](https://9to5google.com/2026/08/31/instagram-ai-generated-influencers-label-update/)
- [Social media updates and new features to know this week — PR Daily](https://www.prdaily.com/social-media-updates-and-new-features-to-know-this-week-32/)
- [Instagram Algorithm 2026: Confirmed Rules vs Myths — Upgrowth](https://upgrowth.in/optimize-instagram-2026-algorithm/)
