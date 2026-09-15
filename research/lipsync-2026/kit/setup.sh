#!/usr/bin/env bash
# Готовит LongCat-Video-Avatar 1.5 к тестовому прогону: клон, патч совместимости,
# проверка импорта без triton/flash-attn. Веса не качает (флаг --weights).
#
#   bash setup.sh [--dir DIR] [--weights]
#
# Требует: git, python3. Для --weights — huggingface-cli и десятки ГБ места.
set -euo pipefail

DIR="./LongCat-Video"
WEIGHTS=0
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="$2"; shift 2 ;;
    --weights) WEIGHTS=1; shift ;;
    *) echo "неизвестный аргумент: $1" >&2; exit 2 ;;
  esac
done

if [[ ! -d "$DIR/.git" ]]; then
  echo "==> клонирую LongCat-Video в $DIR"
  git clone --single-branch --branch main https://github.com/meituan-longcat/LongCat-Video "$DIR"
fi

echo "==> применяю патч совместимости"
# нормализуем в LF: при клоне на Windows git мог переписать патч в CRLF,
# и тогда git apply не сойдётся по контексту с LF-исходниками
PATCH_LF="$(mktemp)"
trap 'rm -f "$PATCH_LF"' EXIT
sed 's/\r$//' "$KIT/longcat-compat.patch" > "$PATCH_LF"

cd "$DIR"
if git apply --check "$PATCH_LF" 2>/dev/null; then
  git apply "$PATCH_LF"
  echo "    патч применён"
elif git apply --reverse --check "$PATCH_LF" 2>/dev/null; then
  echo "    патч уже применён, пропускаю"
else
  echo "    ОШИБКА: патч не накладывается — upstream изменился, сверьте вручную" >&2
  exit 1
fi
cd - >/dev/null

echo "==> проверяю импорт без triton/flash-attn"
python3 "$KIT/../checks/import_check.py" "$DIR" || {
  echo "    импорт не прошёл — смотрите вывод выше" >&2; exit 1; }

if [[ "$WEIGHTS" == "1" ]]; then
  echo "==> качаю веса (долго, десятки ГБ)"
  huggingface-cli download meituan-longcat/LongCat-Video-Avatar-1.5 \
    --local-dir "$DIR/weights/LongCat-Video-Avatar-1.5"
fi

cat <<EOF

Готово. Минимальный замер (1 сегмент = 3.72 c видео, 480p, INT8):

  python3 $KIT/bench_longcat.py --repo $DIR \\
    --checkpoint_dir $DIR/weights/LongCat-Video-Avatar-1.5 \\
    --segments 1 --resolution 480p --vram_budget_gb 24

Вертикаль 9:16 — добавить --vertical. Полный Reel ~32 c — --segments 10.
EOF
