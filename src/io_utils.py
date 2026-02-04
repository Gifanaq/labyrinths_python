from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

from pathlib import Path


def write_lines(lines: Iterable[str], file: str | None) -> None:
    """Записывает строки в файл или выводит в консоль.

    Args:
    ----
        lines: Итерируемый объект со строками
        file: Путь к файлу для записи или None для вывода в консоль

    """
    text = "\n".join(lines)

    if file:
        Path(file).write_text(f"{text}\n", encoding="utf-8")
    else:
        print(text)


def read_lines(file: str) -> list[str]:
    """Читает строки из файла.

    Args:
    ----
        file: Путь к файлу для чтения

    Returns:
    -------
        Список строк из файла

    Raises:
    ------
        FileNotFoundError: Если файл не существует

    """
    p = Path(file)

    if not p.exists():
        error_msg = f"Файл {file} не найден"
        raise FileNotFoundError(error_msg)

    return p.read_text(encoding="utf-8").splitlines()
