#!/usr/bin/env bash
# Готовит LongCat-Video-Avatar 1.5 к тестовому прогону: клон, патч совместимости,
# проверка импорта без triton/flash-attn. Веса не качает (флаг --weights).
#
#   bash setup.sh [--dir DIR] [--deps] [--weights]
#
# Требует: git, python3. Для --weights — huggingface-cli и десятки ГБ места.
set -euo pipefail

DIR="./LongCat-Video"
WEIGHTS=0
DEPS=0
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) DIR="$2"; shift 2 ;;
    --weights) WEIGHTS=1; shift ;;
    --deps) DEPS=1; shift ;;
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

if [[ "$DEPS" == "1" ]]; then
  echo "==> ставлю зависимости без flash-attn"
  # flash-attn собирается из исходников и на Windows не встаёт; после патча он не обязателен
  for req in requirements.txt requirements_avatar.txt; do
    [[ -f "$DIR/$req" ]] || continue
    nofa="$DIR/${req%.txt}-nofa.txt"
    # выкидываем flash-attn (не собирается на Windows) и torch-пины: иначе pip
    # подменит рабочую CUDA-сборку колесом с PyPI, которое под Windows без CUDA
    grep -v -E '^[[:space:]]*(flash[-_]attn|torch|torchvision|torchaudio)([=<>!~[:space:]]|$)' \
      "$DIR/$req" > "$nofa"
    CONSTRAINTS="$DIR/constraints-torch.txt"
    python3 "$KIT/torch_constraints.py" > "$CONSTRAINTS" 2>/dev/null || true
    PIP_C=()
    [[ -s "$CONSTRAINTS" ]] && PIP_C=(-c "$CONSTRAINTS")
    if ! python3 -m pip install -r "$nofa" "${PIP_C[@]}"; then
      # pip install -r ставит всё или ничего: один плохой пин блокирует файл,
      # поэтому добиваем по одному и сообщаем только про реально упавшие
      echo "    массовая установка $req не прошла, ставлю по одному" >&2
      failed=()
      while IFS= read -r line; do
        pkg="$(echo "$line" | tr -d '[:space:]')"
        [[ -z "$pkg" || "$pkg" == \#* ]] && continue
        python3 -m pip install "$pkg" "${PIP_C[@]}" || failed+=("$pkg")
      done < "$nofa"
      [[ ${#failed[@]} -gt 0 ]] && echo "    не установлено из $req: ${failed[*]}" >&2
    fi
  done
fi

echo "==> проверяю импорт без triton/flash-attn"
set +e
python3 "$KIT/../checks/import_check.py" "$DIR"
IMPORT_RC=$?
set -e
if [[ "$IMPORT_RC" == "3" ]]; then
  echo "    зависимости ещё не установлены — повторите после --deps" >&2
elif [[ "$IMPORT_RC" != "0" ]]; then
  echo "    импорт не прошёл — смотрите вывод выше" >&2; exit 1
fi

echo "==> преконтроль окружения"
python3 "$KIT/preflight.py" --repo "$DIR" || true   # информативно, не обрывает подготовку

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
