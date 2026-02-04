from pathlib import Path

import pytest

from src.io_utils import read_lines, write_lines


def test_write_lines_to_file(tmp_path: Path) -> None:
    """Проверяет запись строк в файл."""
    file = tmp_path / "test_output.txt"
    lines = ["line 1", "line 2", "line 3"]

    write_lines(lines, str(file))

    assert file.exists()
    assert file.read_text(encoding="utf-8") == "line 1\nline 2\nline 3\n"


def test_write_lines_to_stdout(capfd: pytest.CaptureFixture) -> None:
    """Проверяет вывод строк в стандартный вывод."""
    lines = ["line 1", "line 2", "line 3"]

    write_lines(lines, None)

    captured = capfd.readouterr()
    assert captured.out == "line 1\nline 2\nline 3\n"


def test_read_lines_invalid_file(tmp_path: Path) -> None:
    """Проверяет обработку ошибки при чтении несуществующего файла."""
    missing_file = tmp_path / "missing_file.txt"

    with pytest.raises(FileNotFoundError):
        read_lines(str(missing_file))


def test_read_lines_valid_file(tmp_path: Path) -> None:
    """Проверяет чтение строк из существующего файла."""
    file = tmp_path / "test_input.txt"
    lines = ["line 1", "line 2", "line 3"]
    file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = read_lines(str(file))
    assert result == lines
