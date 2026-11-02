"""Tests for explorer helpers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from photo_converter.file_browser import _human_size, _is_image, _safe_listdir
from photo_converter.i18n import LANG_EN, LANG_RU, STRINGS


def test_is_image(tmp_path: Path) -> None:
    img = tmp_path / "a.jpg"
    img.write_bytes(b"x")
    assert _is_image(img)
    assert not _is_image(tmp_path / "a.txt")


def test_safe_listdir(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    Image.new("RGB", (8, 8), (1, 2, 3)).save(tmp_path / "p.png")
    (tmp_path / "notes.txt").write_text("nope")
    dirs, files = _safe_listdir(tmp_path)
    assert any(d.name == "sub" for d in dirs)
    assert any(f.name == "p.png" for f in files)
    assert not any(f.name == "notes.txt" for f in files)


def test_human_size() -> None:
    assert _human_size(500).endswith("B")
    assert "KB" in _human_size(2048)


def test_explorer_i18n_keys_match() -> None:
    keys = {k for k in STRINGS[LANG_EN] if k.startswith("explorer_")}
    assert keys
    assert keys <= set(STRINGS[LANG_RU])
