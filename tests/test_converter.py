from pathlib import Path

import pytest

from heic2jpg.cli import main
from heic2jpg.converter import find_heic_files, output_path_for_file, parse_resize


def test_parse_resize_accepts_width_by_height() -> None:
    assert parse_resize("1920x1080") == (1920, 1080)


@pytest.mark.parametrize("value", ["", None])
def test_parse_resize_empty(value: str | None) -> None:
    assert parse_resize(value) is None


@pytest.mark.parametrize("value", ["1920", "0x1080", "ax1080"])
def test_parse_resize_rejects_invalid(value: str) -> None:
    with pytest.raises(ValueError):
        parse_resize(value)


def test_find_heic_files_non_recursive(tmp_path: Path) -> None:
    (tmp_path / "a.HEIC").write_bytes(b"not really heic")
    (tmp_path / "b.heif").write_bytes(b"not really heif")
    (tmp_path / "c.jpg").write_bytes(b"jpg")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "d.heic").write_bytes(b"nested")

    assert [path.name for path in find_heic_files(tmp_path)] == ["a.HEIC", "b.heif"]


def test_find_heic_files_recursive(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (tmp_path / "a.heic").write_bytes(b"root")
    (nested / "b.heic").write_bytes(b"nested")

    assert [path.relative_to(tmp_path) for path in find_heic_files(tmp_path, recursive=True)] == [
        Path("a.heic"),
        Path("nested/b.heic"),
    ]


def test_output_path_preserves_tree_when_recursive(tmp_path: Path) -> None:
    source_root = tmp_path / "input"
    output_root = tmp_path / "output"
    source = source_root / "nested" / "image.heic"

    assert (
        output_path_for_file(
            source,
            source_root=source_root,
            output_root=output_root,
            recursive=True,
        )
        == output_root / "nested" / "image.jpg"
    )


def test_cli_reports_missing_directory(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing = tmp_path / "missing"

    assert main([str(missing)]) == 1
    captured = capsys.readouterr()
    assert "Directory does not exist" in captured.out
