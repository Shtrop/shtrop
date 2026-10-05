#!/usr/bin/env python3
"""Диагностика блокеров публикации с конкретным исправлением по каждому.

Закрывает три блокера, найденных разбором воронки:

  A. МЕДИА-ХОСТИНГ — Graph API забирает медиа по публичному HTTPS-URL.
     Проверяет кандидата на доступность, валидность сертификата, тип и
     размер содержимого ровно так, как это сделает Instagram.

  B. CAPTION GUARD — отличает «плохой текст» от «гейту не передали
     доказательства»: считает, какие evidence-ключи отсутствуют всегда.

  C. ФОРМАТ МЕДИА — считает фактическое соотношение сторон и целевые
     размеры под ближайшее поддерживаемое; находит неподдерживаемые типы.

Только чтение и сетевая проверка указанного URL. Ничего не публикует,
не меняет состояние студии и не снимает HOLD.

Примеры:
    python publish_doctor.py --studio "D:\\AI_CONTENT\\Sofia"
    python publish_doctor.py --media-url https://media.example.com/reel.mp4
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import ssl
import struct
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _console import force_utf8  # noqa: E402
from ingest_insights import discover  # noqa: E402

# Требования Instagram Graph API к медиа-источнику.
ALLOWED_IMAGE_TYPES = ("image/jpeg",)
ALLOWED_VIDEO_TYPES = ("video/mp4", "video/quicktime")
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_REEL_BYTES = 1024 * 1024 * 1024

# Поддерживаемые соотношения сторон (ширина / высота).
SUPPORTED_RATIOS = {
    "4:5 (лента, максимум площади)": 4 / 5,
    "1:1 (квадрат)": 1.0,
    "1.91:1 (горизонт)": 1.91,
    "9:16 (Reels и Stories)": 9 / 16,
}
# Требования Instagram к разрешению. Соотношение можно выдержать и в 480p,
# но платформа пережимает или отклоняет такое видео, а гейты качества
# отбраковывают его ещё раньше.
MIN_VIDEO_WIDTH = 540
RECOMMENDED_VIDEO_WIDTH = 1080
MIN_IMAGE_WIDTH = 320
RECOMMENDED_IMAGE_WIDTH = 1080

# Служебные артефакты рендера: контент-требования к ним не применяются.
SERVICE_FILE_HINTS = ("contact_sheet", "contactsheet", "_thumb", "thumbnail",
                      "preview", "proxy", "_mask", "_debug", "poster")

EVIDENCE_PATTERN = re.compile(r"evidence_missing:([a-z_]+)", re.IGNORECASE)
GATE_PATTERN = re.compile(r"gate_failed:([a-z_]+)", re.IGNORECASE)


def check_media_url(url: str) -> int:
    """Проверяет URL так, как это сделает Instagram при создании контейнера."""
    print(f"\n[A] МЕДИА-ХОСТИНГ — проверка {url}")
    if any(ch in url for ch in "<>"):
        print("    FAIL: в URL остались угловые скобки — это шаблон, а не адрес.")
        print("    Подставить реальный домен и путь к файлу.")
        return 1
    try:
        url.encode("ascii")
    except UnicodeEncodeError:
        print("    FAIL: в URL есть не-ASCII символы (кириллица или подобное).")
        print("    Graph API принимает только ASCII-адреса; интернационализированный")
        print("    домен нужно записать в punycode, а путь — в percent-encoding.")
        return 1
    if not url.lower().startswith("https://"):
        print("    FAIL: Graph API принимает только HTTPS. Локальные файлы и HTTP не годятся.")
        return 1

    context = ssl.create_default_context()
    request = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "facebookexternalhit/1.1"})
    try:
        with urllib.request.urlopen(request, timeout=20, context=context) as response:
            status = response.status
            headers = {k.lower(): v for k, v in response.headers.items()}
    except urllib.error.HTTPError as exc:
        print(f"    FAIL: HTTP {exc.code}. Медиа должно отдаваться анонимно, без авторизации.")
        return 1
    except Exception as exc:
        # urllib заворачивает ошибку сертификата в URLError, поэтому проверяем
        # причину, а не только тип: иначе самая частая поломка получит общий текст.
        reason = getattr(exc, "reason", None)
        if isinstance(exc, ssl.SSLCertVerificationError) or \
                isinstance(reason, ssl.SSLCertVerificationError) or \
                "CERTIFICATE_VERIFY_FAILED" in str(exc):
            detail = getattr(reason, "reason", None) or str(reason or exc)
            print(f"    FAIL: сертификат не проходит проверку — {detail}")
            print("    Это та же ошибка, что в журнале как [X509] PEM lib (_ssl.c).")
            print("    Нужен домен с доверенным сертификатом, а не самоподписанный")
            print("    или туннельный: Instagram проверяет цепочку и молча отказывает.")
            return 1
        print(f"    FAIL: недоступно — {type(exc).__name__}: {exc}")
        print("    Временный туннель не годится как production-хост: он отваливается")
        print("    между созданием контейнера и его публикацией.")
        return 1

    content_type = headers.get("content-type", "").split(";")[0].strip().lower()
    length = int(headers.get("content-length") or 0)
    print(f"    PASS: HTTP {status}, тип {content_type or 'не указан'}, "
          f"размер {length / 1024 / 1024:.2f} МБ" if length else
          f"    PASS: HTTP {status}, тип {content_type or 'не указан'}, размер не указан")

    problems = []
    if content_type in ALLOWED_IMAGE_TYPES:
        if length > MAX_IMAGE_BYTES:
            problems.append(f"изображение больше {MAX_IMAGE_BYTES // 1024 // 1024} МБ")
    elif content_type in ALLOWED_VIDEO_TYPES:
        if length > MAX_REEL_BYTES:
            problems.append("видео больше 1 ГБ")
    elif content_type:
        problems.append(f"тип {content_type} не принимается: нужен "
                        f"{' / '.join(ALLOWED_IMAGE_TYPES + ALLOWED_VIDEO_TYPES)}")
    else:
        problems.append("сервер не отдаёт Content-Type — Graph API отклонит медиа")

    if headers.get("content-encoding"):
        problems.append("включено сжатие ответа: для медиа его быть не должно")

    for problem in problems:
        print(f"    FAIL: {problem}")
    if not problems:
        print("    Хост пригоден как production media host.")
    return 1 if problems else 0


def analyse_caption_guard(paths: list[Path]) -> int:
    """Отличает проблему качества текста от непереданных доказательств."""
    print("\n[B] CAPTION GUARD — что именно не проходит")
    evidence = Counter()
    gates = Counter()
    demotions = 0
    caption_failures = 0
    total_errors = 0

    for path in paths:
        try:
            connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        except sqlite3.Error:
            continue
        try:
            tables = [row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view')")]
            for table in tables:
                columns = {c[1].lower() for c in connection.execute(f'PRAGMA table_info("{table}")')}
                for column in ("error_message", "failure_reason", "detail"):
                    if column not in columns:
                        continue
                    try:
                        rows = connection.execute(f'SELECT "{column}" FROM "{table}"').fetchall()
                    except sqlite3.Error:
                        continue
                    for (value,) in rows:
                        if not value:
                            continue
                        text = str(value)
                        total_errors += 1
                        evidence.update(m.lower() for m in EVIDENCE_PATTERN.findall(text))
                        gates.update(m.lower() for m in GATE_PATTERN.findall(text))
                        if "demoted to review" in text:
                            demotions += 1
                        if "no_caption_passed_guard" in text:
                            caption_failures += 1
        finally:
            connection.close()

    if not total_errors:
        print("    NOT_MEASURED: записей с причинами отбраковки не найдено.")
        return 1

    print(f"    отбраковок подписи (no_caption_passed_guard): {caption_failures}")
    print(f"    разжалований одобренного обратно в review: {demotions}")
    if gates:
        print("    какие гейты валят:")
        for name, count in gates.most_common():
            print(f"      {name:<28} ×{count}")
    if evidence:
        print("    каких доказательств не хватает:")
        for name, count in evidence.most_common():
            print(f"      evidence_missing:{name:<20} ×{count}")

    print("\n    ДИАГНОЗ:")
    if len(evidence) >= 5:
        counts = sorted(evidence.values(), reverse=True)
        print(f"      Отсутствует не отдельный артефакт, а {len(evidence)} ключей сразу "
              f"(от {counts[-1]} до {counts[0]} раз).")
        print("      Столько доказательств не может отсутствовать по содержательной")
        print("      причине: не работает сама цепочка сбора evidence, а не подписи.")
    if evidence and demotions:
        print("      Гейт не получает артефакты, которые требует. Это дефект передачи")
        print("      доказательств между генерацией и гейтом, а не качество текста:")
        print("      отсутствующие ключи одни и те же, а разжалование срабатывает уже")
        print("      ПОСЛЕ одобрения.")
        print("    ИСПРАВЛЕНИЕ:")
        print("      1. Найти в студии код, который формирует evidence для caption guard.")
        for name, _ in evidence.most_common(4):
            print(f"         Обязан заполняться ключ: {name}")
        print("      2. Проверить, что артефакты пишутся ДО вызова гейта и по тому же")
        print("         пути, откуда гейт их читает.")
        print("      3. Порог трогать в последнюю очередь: пока доказательств нет,")
        print("         любой порог даёт отказ.")
    elif caption_failures:
        print("      Доказательства передаются, отбраковка идёт по содержанию.")
        print("      Смотреть примеры отклонённых подписей и калибровать порог.")
    return 1


def image_size(path: Path) -> tuple[int, int] | None:
    """Размеры изображения из заголовка, без внешних зависимостей."""
    try:
        with path.open("rb") as handle:
            head = handle.read(32)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                width, height = struct.unpack(">II", head[16:24])
                return width, height
            if head[:2] == b"\xff\xd8":  # JPEG: искать SOF-маркер
                handle.seek(2)
                while True:
                    marker = handle.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        return None
                    size = struct.unpack(">H", handle.read(2))[0]
                    if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                        data = handle.read(5)
                        height, width = struct.unpack(">HH", data[1:5])
                        return width, height
                    handle.seek(size - 2, 1)
    except (OSError, struct.error):
        return None
    return None


def video_size(path: Path) -> tuple[int, int] | None:
    """Размеры видео через ffprobe, если он есть в системе."""
    if not shutil.which("ffprobe"):
        return None
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
             "stream=width,height", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=30)
        streams = json.loads(result.stdout).get("streams") or []
        if streams:
            return int(streams[0]["width"]), int(streams[0]["height"])
    except (subprocess.SubprocessError, json.JSONDecodeError, KeyError, ValueError):
        return None
    return None


def nearest_ratio(width: int, height: int) -> tuple[str, float, float]:
    actual = width / height
    name, target = min(SUPPORTED_RATIOS.items(), key=lambda item: abs(actual - item[1]))
    return name, target, abs(actual - target)


def analyse_media_format(media_dir: Path) -> int:
    """Считает фактическое соотношение и целевые размеры под ближайшее поддерживаемое."""
    print(f"\n[C] ФОРМАТ МЕДИА — проверка файлов в {media_dir}")
    if not media_dir.exists():
        print("    BLOCKED: каталог не найден. Указать через --media-dir.")
        return 1

    suffixes = {".jpg", ".jpeg", ".png", ".mp4", ".mov"}
    all_files = [p for p in media_dir.rglob("*") if p.suffix.lower() in suffixes]
    service = [p for p in all_files if any(hint in p.name.lower() for hint in SERVICE_FILE_HINTS)]
    files = [p for p in all_files if p not in service][:200]
    if service:
        print(f"    пропущено служебных артефактов рендера: {len(service)} "
              f"(контактные листы, превью, прокси)")
    if not files:
        print("    NOT_MEASURED: публикуемых медиафайлов не найдено.")
        return 1

    ratio_bad, resolution_bad = 0, 0
    for path in files:
        is_video = path.suffix.lower() in (".mp4", ".mov")
        size = video_size(path) if is_video else image_size(path)
        if not size:
            continue
        width, height = size
        name, target, delta = nearest_ratio(width, height)
        problems = []
        if delta > 0.01:
            ratio_bad += 1
            target_height = round(width / target)
            target_width = round(height * target)
            problems.append(f"соотношение {width / height:.4f}, ближайшее {name} "
                            f"(={target:.4f}), delta={delta:.4f}")
            problems.append(f"под {name}: либо {width}×{target_height}, "
                            f"либо {target_width}×{height}")

        minimum = MIN_VIDEO_WIDTH if is_video else MIN_IMAGE_WIDTH
        recommended = RECOMMENDED_VIDEO_WIDTH if is_video else RECOMMENDED_IMAGE_WIDTH
        if width < minimum:
            resolution_bad += 1
            # Рекомендация закрывает оба дефекта сразу: правильное соотношение
            # в рекомендованном разрешении, а не масштабирование текущей ошибки.
            scaled_height = round(recommended / target)
            problems.append(f"ширина {width} ниже минимума {minimum}: платформа отклонит "
                            f"или сильно пережмёт")
            problems.append(f"целевой рендер под {name}: {recommended}×{scaled_height}")
        if problems:
            print(f"    {path.name}: {width}×{height}")
            for line in problems:
                print(f"      {line}")

    print()
    if resolution_bad:
        print(f"    Файлов ниже минимального разрешения: {resolution_bad}.")
        print("    Это отдельная причина отбраковки, независимая от соотношения:")
        print("    качественные гейты и сама платформа отсеивают низкое разрешение")
        print("    раньше, чем дело доходит до публикации.")
    if ratio_bad:
        print(f"    Файлов с неверным соотношением: {ratio_bad}.")
        print("    Для Reels обязательно 9:16 — иначе нефолловерского охвата не будет.")
    if not (ratio_bad or resolution_bad):
        print(f"    PASS: все {len(files)} публикуемых файлов в допуске.")
    return 1 if (ratio_bad or resolution_bad) else 0


def main() -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--studio", type=Path, help="корень студии")
    parser.add_argument("--media-url", help="проверить кандидата в production media host")
    parser.add_argument("--media-dir", type=Path, help="каталог с готовым медиа")
    args = parser.parse_args()

    if not any((args.studio, args.media_url, args.media_dir)):
        parser.error("нужен хотя бы один из --studio, --media-url, --media-dir")

    print("=== Диагностика блокеров публикации ===")
    codes = []
    if args.media_url:
        codes.append(check_media_url(args.media_url))
    else:
        print("\n[A] МЕДИА-ХОСТИНГ — пропущен: не задан --media-url")
        print("    Журнал показывает, что публикация срывается именно здесь.")
        print("    Проверить кандидата: --media-url https://<домен>/<файл>.mp4")

    if args.studio:
        journals = [p for p in discover(args.studio)
                    if p.suffix.lower() in (".db", ".sqlite", ".sqlite3")]
        if journals:
            codes.append(analyse_caption_guard(journals))
        else:
            print("\n[B] CAPTION GUARD — журналов не найдено")

    if args.media_dir:
        codes.append(analyse_media_format(args.media_dir))

    print("\n" + "=" * 60)
    print("Диагностика ничего не изменила: публикация требует отдельного решения")
    print("владельца и прохождения Master Publish Gate.")
    return 0 if codes and all(code == 0 for code in codes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
