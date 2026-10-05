"""Единая настройка вывода для всех инструментов.

На Windows дочерний процесс получает для пайпа кодировку локали (cp1251), в
которой нет ни `→`, ни многих других символов отчёта. Python падает с
UnicodeEncodeError, вывод оказывается пустым, а вызывающая сторона принимает
это за «данных нет». Здесь вывод принудительно переводится в UTF-8.
"""

from __future__ import annotations

import os
import subprocess
import sys


def force_utf8() -> None:
    """Перевести stdout/stderr в UTF-8, чтобы отчёт не падал на символах."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass  # поток уже перенастроен или не поддерживает это


def child_env() -> dict:
    """Окружение для дочернего процесса Python с UTF-8 выводом."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_tool(args: list[str]) -> subprocess.CompletedProcess:
    """Запустить инструмент так, чтобы его вывод точно дошёл целиком."""
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=child_env())
