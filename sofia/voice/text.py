"""Text measurement used by the pronunciation and semantic critics.

All of this is deterministic and exact: word error rate via Levenshtein
alignment, number/name/borrowed-word preservation, and per-word localisation of
the failure so the repair agent can regenerate a single word instead of the
whole clip.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

from sofia.voice.contracts import Language

_WORD_RE = re.compile(r"[^\W\d_]+|\d+", re.UNICODE)

#: Digits written as words, so "25" vs "двадцать пять" is not counted as an error.
_NUMBER_WORDS: dict[str, dict[int, str]] = {
    "ru": {
        0: "ноль", 1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять",
        6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять",
        11: "одиннадцать", 12: "двенадцать", 13: "тринадцать", 14: "четырнадцать",
        15: "пятнадцать", 16: "шестнадцать", 17: "семнадцать", 18: "восемнадцать",
        19: "девятнадцать", 20: "двадцать", 30: "тридцать", 40: "сорок",
        50: "пятьдесят", 60: "шестьдесят", 70: "семьдесят", 80: "восемьдесят",
        90: "девяносто", 100: "сто",
    },
    "uk": {
        0: "нуль", 1: "один", 2: "два", 3: "три", 4: "чотири", 5: "п'ять",
        6: "шість", 7: "сім", 8: "вісім", 9: "дев'ять", 10: "десять",
        11: "одинадцять", 12: "дванадцять", 13: "тринадцять", 14: "чотирнадцять",
        15: "п'ятнадцять", 16: "шістнадцять", 17: "сімнадцять", 18: "вісімнадцять",
        19: "дев'ятнадцять", 20: "двадцять", 30: "тридцять", 40: "сорок",
        50: "п'ятдесят", 60: "шістдесят", 70: "сімдесят", 80: "вісімдесят",
        90: "дев'яносто", 100: "сто",
    },
    "en": {
        0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
        6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
        11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
        15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
        19: "nineteen", 20: "twenty", 30: "thirty", 40: "forty",
        50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty",
        90: "ninety", 100: "hundred",
    },
}

#: Script ranges used to detect that the wrong language was synthesised.
_CYRILLIC = re.compile(r"[Ѐ-ӿ]")
_LATIN = re.compile(r"[A-Za-z]")
#: Letters that only exist in Ukrainian, not Russian, and vice versa.
_UA_ONLY = set("іїєґІЇЄҐ")
_RU_ONLY = set("ыэъёЫЭЪЁ")


def normalize(text: str, language: Language = Language.RU) -> str:
    """Lowercase, strip accents-as-stress-marks and collapse punctuation."""

    text = unicodedata.normalize("NFKC", text)
    # U+0301 is the combining acute used to mark stress in RU/UA scripts.
    text = text.replace("́", "").replace("+", "")
    text = text.replace("ё", "е").replace("Ё", "Е") if language is Language.RU else text
    return " ".join(_WORD_RE.findall(text.lower()))


def tokenize(text: str, language: Language = Language.RU) -> list[str]:
    return normalize(text, language).split()


def expand_numbers(tokens: Sequence[str], language: Language) -> list[str]:
    """Replace bare integers with their spoken form for fair comparison."""

    table = _NUMBER_WORDS.get(language.value, {})
    out: list[str] = []
    for tok in tokens:
        if tok.isdigit() and table:
            out.extend(_spell_int(int(tok), table))
        else:
            out.append(tok)
    return out


def _spell_int(value: int, table: dict[int, str]) -> list[str]:
    if value in table:
        return [table[value]]
    if value < 100:
        tens, ones = divmod(value, 10)
        parts = []
        if tens * 10 in table:
            parts.append(table[tens * 10])
        if ones and ones in table:
            parts.append(table[ones])
        return parts or [str(value)]
    return [str(value)]


@dataclass(frozen=True)
class Alignment:
    """Word-level alignment between reference and hypothesis."""

    substitutions: tuple[tuple[str, str], ...] = ()
    deletions: tuple[str, ...] = ()
    insertions: tuple[str, ...] = ()
    reference_len: int = 0

    @property
    def errors(self) -> int:
        return len(self.substitutions) + len(self.deletions) + len(self.insertions)

    @property
    def wer(self) -> float:
        if self.reference_len == 0:
            return 0.0 if self.errors == 0 else 1.0
        return self.errors / self.reference_len

    def bad_words(self) -> list[str]:
        """Reference words that were mangled — the repair loci."""
        return [ref for ref, _ in self.substitutions] + list(self.deletions)


def align(reference: Sequence[str], hypothesis: Sequence[str]) -> Alignment:
    """Levenshtein alignment over words, keeping the edit operations."""

    n, m = len(reference), len(hypothesis)
    # dp[i][j] = (cost, op) where op in {'=', 'S', 'D', 'I'}
    dp: list[list[int]] = [[0] * (m + 1) for _ in range(n + 1)]
    bt: list[list[str]] = [[""] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i
        bt[i][0] = "D"
    for j in range(1, m + 1):
        dp[0][j] = j
        bt[0][j] = "I"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if reference[i - 1] == hypothesis[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                bt[i][j] = "="
                continue
            sub = dp[i - 1][j - 1] + 1
            dele = dp[i - 1][j] + 1
            ins = dp[i][j - 1] + 1
            best = min(sub, dele, ins)
            dp[i][j] = best
            bt[i][j] = "S" if best == sub else ("D" if best == dele else "I")

    subs: list[tuple[str, str]] = []
    dels: list[str] = []
    inss: list[str] = []
    i, j = n, m
    while i > 0 or j > 0:
        op = bt[i][j]
        if op == "=":
            i, j = i - 1, j - 1
        elif op == "S":
            subs.append((reference[i - 1], hypothesis[j - 1]))
            i, j = i - 1, j - 1
        elif op == "D":
            dels.append(reference[i - 1])
            i -= 1
        else:
            inss.append(hypothesis[j - 1])
            j -= 1
    subs.reverse()
    dels.reverse()
    inss.reverse()
    return Alignment(tuple(subs), tuple(dels), tuple(inss), n)


def word_error_rate(
    reference: str, hypothesis: str, language: Language = Language.RU
) -> Alignment:
    """WER between the script and what ASR heard, numbers expanded."""

    ref = expand_numbers(tokenize(reference, language), language)
    hyp = expand_numbers(tokenize(hypothesis, language), language)
    return align(ref, hyp)


@dataclass(frozen=True)
class ContentCheck:
    """Which meaning-bearing items survived synthesis."""

    missing_numbers: tuple[str, ...] = ()
    missing_names: tuple[str, ...] = ()
    missing_required: tuple[str, ...] = ()
    extra_content_words: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not (
            self.missing_numbers
            or self.missing_names
            or self.missing_required
            or self.extra_content_words
        )


def extract_numbers(text: str) -> list[str]:
    return re.findall(r"\d+(?:[.,]\d+)?%?", text)


def extract_names(text: str, language: Language) -> list[str]:
    """Capitalised tokens that are not sentence-initial — a proper-name proxy."""

    names: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        tokens = _WORD_RE.findall(sentence)
        for idx, tok in enumerate(tokens):
            if idx == 0:
                continue
            if tok[:1].isupper() and len(tok) > 1:
                names.append(tok.lower())
    return names


#: Words an ASR transcript may legitimately add when expanding symbols.
_EXPANSION_WORDS: dict[str, frozenset[str]] = {
    "ru": frozenset({"процент", "процента", "процентов", "рубль", "рубля", "рублей",
                     "градус", "градуса", "градусов", "минус", "плюс"}),
    "uk": frozenset({"відсоток", "відсотка", "відсотків", "гривня", "гривні",
                     "градус", "градуса", "градусів", "мінус", "плюс"}),
    "en": frozenset({"percent", "degrees", "degree", "dollars", "dollar",
                     "minus", "plus"}),
}


def check_content_preserved(
    script: str,
    transcript: str,
    language: Language,
    *,
    required: Iterable[str] = (),
    aliases: Mapping[str, str] | None = None,
) -> ContentCheck:
    """Verify synthesis did not drop or invent meaning-bearing content.

    ``aliases`` lets the VoiceDirector declare an intended rendering (for
    example the name ``Sofia`` spoken as ``Софи`` in a RU clip) so a correct
    transliteration is not reported as a dropped name.
    """

    alias_map = {
        normalize(k, language): normalize(v, language)
        for k, v in (aliases or {}).items()
    }
    hyp_tokens = set(expand_numbers(tokenize(transcript, language), language))
    hyp_raw = normalize(transcript, language)

    missing_numbers = []
    for num in extract_numbers(script):
        digits = num.rstrip("%").replace(",", ".")
        spoken = set()
        if digits.isdigit():
            spoken = set(_spell_int(int(digits), _NUMBER_WORDS.get(language.value, {})))
        if digits not in hyp_tokens and not (spoken and spoken & hyp_tokens):
            missing_numbers.append(num)

    missing_names = []
    for name in extract_names(script, language):
        if name in hyp_tokens:
            continue
        alias = alias_map.get(name)
        if alias and all(part in hyp_tokens for part in alias.split()):
            continue
        missing_names.append(name)
    missing_required = [
        r for r in required if normalize(r, language) not in hyp_raw
    ]

    ref_tokens = set(expand_numbers(tokenize(script, language), language))
    for alias in alias_map.values():
        ref_tokens.update(alias.split())
    allowed_extra = _EXPANSION_WORDS.get(language.value, frozenset())
    extra = [
        t for t in hyp_tokens - ref_tokens if len(t) > 3 and t not in allowed_extra
    ]

    return ContentCheck(
        missing_numbers=tuple(missing_numbers),
        missing_names=tuple(dict.fromkeys(missing_names)),
        missing_required=tuple(missing_required),
        extra_content_words=tuple(sorted(extra)),
    )


def detect_script_language(text: str) -> set[str]:
    """Which language families the *written* form belongs to.

    Used by the identity/pronunciation critics to catch a clip synthesised in
    the wrong language (e.g. RU text read by a UA model, or Latin leakage).
    """

    found: set[str] = set()
    chars = set(text)
    if _CYRILLIC.search(text):
        found.add("cyrillic")
    if _LATIN.search(text):
        found.add("latin")
    if chars & _UA_ONLY:
        found.add("uk")
    if chars & _RU_ONLY:
        found.add("ru")
    return found


def language_mismatch(script: str, transcript: str, language: Language) -> str:
    """Return a human-readable mismatch reason, or an empty string."""

    hyp = detect_script_language(transcript)
    if not hyp:
        return "transcript contains no recognisable script"
    if language is Language.EN:
        if "cyrillic" in hyp and "latin" not in hyp:
            return "EN script was transcribed as Cyrillic"
    else:
        if "latin" in hyp and "cyrillic" not in hyp:
            return f"{language.label} script was transcribed as Latin"
    if language is Language.UA and "ru" in hyp and "uk" not in hyp:
        return "UA clip transcribed with Russian-only letters (likely RU voice)"
    if language is Language.RU and "uk" in hyp and "ru" not in hyp:
        return "RU clip transcribed with Ukrainian-only letters (likely UA voice)"
    return ""


def stress_violations(script: str, lexicon: dict[str, str], transcript: str) -> list[str]:
    """Words whose required stressed form did not survive.

    ``lexicon`` maps a word to its required spoken form (for example a stress
    marked variant or an explicit transliteration of a borrowed word).
    """

    hyp = normalize(transcript)
    bad: list[str] = []
    for word, required_form in lexicon.items():
        if normalize(word) in normalize(script) and normalize(required_form) not in hyp:
            bad.append(word)
    return bad
