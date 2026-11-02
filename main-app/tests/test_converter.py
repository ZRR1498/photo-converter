"""Unit tests for the conversion engine."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from photo_converter.converter import (
    collect_images,
    convert_many,
    convert_one,
    format_quality_hint,
)
from photo_converter.formats import INPUT_EXTENSIONS, OUTPUT_FORMAT_LABELS, is_supported_input


@pytest.fixture()
def sample_images(tmp_path: Path) -> list[Path]:
    files: list[Path] = []

    rgb = Image.new("RGB", (64, 48), color=(220, 40, 40))
    p = tmp_path / "red.jpg"
    rgb.save(p, format="JPEG", quality=90)
    files.append(p)

    rgba = Image.new("RGBA", (40, 40), color=(20, 180, 80, 128))
    p = tmp_path / "green_alpha.png"
    rgba.save(p, format="PNG")
    files.append(p)

    gray = Image.new("L", (32, 32), color=128)
    p = tmp_path / "gray.bmp"
    gray.save(p, format="BMP")
    files.append(p)

    webp = Image.new("RGB", (20, 20), color=(30, 30, 200))
    p = tmp_path / "blue.webp"
    webp.save(p, format="WEBP", quality=90)
    files.append(p)

    # Nested folder
    nested = tmp_path / "album"
    nested.mkdir()
    nest_img = Image.new("RGB", (16, 16), color=(255, 255, 0))
    p = nested / "nested.tiff"
    nest_img.save(p, format="TIFF")
    files.append(p)

    return files


def test_is_supported_input() -> None:
    assert is_supported_input(".JPG")
    assert is_supported_input(".heic")
    assert not is_supported_input(".txt")
    assert ".png" in INPUT_EXTENSIONS


def test_collect_images_from_dir_and_files(sample_images: list[Path], tmp_path: Path) -> None:
    # Direct files + recursive dir
    found = collect_images([sample_images[0], tmp_path])
    names = {p.name for p in found}
    assert "red.jpg" in names
    assert "nested.tiff" in names
    assert len(found) >= 5


def test_convert_jpeg_to_png_preserves_original(sample_images: list[Path], tmp_path: Path) -> None:
    src = next(p for p in sample_images if p.suffix == ".jpg")
    original_bytes = src.read_bytes()
    out_dir = tmp_path / "out"
    result = convert_one(src, out_dir, "PNG", quality=95)

    assert result.success
    assert result.destination is not None
    assert result.destination.exists()
    assert result.destination.suffix == ".png"
    assert result.destination.stem == "red"
    # Original untouched
    assert src.read_bytes() == original_bytes
    with Image.open(result.destination) as img:
        assert img.format == "PNG"
        assert img.size == (64, 48)


def test_rgba_to_jpeg_flattens_alpha(sample_images: list[Path], tmp_path: Path) -> None:
    src = next(p for p in sample_images if p.name.startswith("green"))
    out_dir = tmp_path / "out_jpeg"
    result = convert_one(src, out_dir, "JPEG", quality=95)
    assert result.success
    with Image.open(result.destination) as img:
        assert img.mode == "RGB"
        assert img.format == "JPEG"


def test_convert_many_and_name_collision(sample_images: list[Path], tmp_path: Path) -> None:
    src = next(p for p in sample_images if p.suffix == ".jpg")
    out_dir = tmp_path / "batch"
    first = convert_one(src, out_dir, "WEBP", quality=100, overwrite=False)
    second = convert_one(src, out_dir, "WEBP", quality=100, overwrite=False)
    assert first.success and second.success
    assert first.destination != second.destination
    assert second.destination is not None
    assert "_1" in second.destination.stem


def test_overwrite_flag(sample_images: list[Path], tmp_path: Path) -> None:
    src = next(p for p in sample_images if p.suffix == ".jpg")
    out_dir = tmp_path / "ow"
    a = convert_one(src, out_dir, "PNG", overwrite=True)
    b = convert_one(src, out_dir, "PNG", overwrite=True)
    assert a.destination == b.destination


def test_convert_many_progress(sample_images: list[Path], tmp_path: Path) -> None:
    events: list[tuple[int, int, str]] = []
    summary = convert_many(
        sample_images[:3],
        tmp_path / "many",
        "PNG",
        progress=lambda c, t, n: events.append((c, t, n)),
    )
    assert summary.succeeded == 3
    assert summary.failed == 0
    assert len(events) == 3


def test_bad_file_reports_error(tmp_path: Path) -> None:
    bogus = tmp_path / "fake.jpg"
    bogus.write_bytes(b"not-an-image")
    result = convert_one(bogus, tmp_path / "out", "PNG")
    assert not result.success
    assert result.error


def test_quality_hints() -> None:
    assert "Lossless" in format_quality_hint("PNG")
    assert "JPEG" in format_quality_hint("JPEG")
    for label in OUTPUT_FORMAT_LABELS:
        assert isinstance(format_quality_hint(label), str)


def test_heic_to_jpeg_when_available(tmp_path: Path) -> None:
    pytest.importorskip("pillow_heif")
    from pillow_heif import register_heif_opener

    register_heif_opener()
    src = tmp_path / "phone.heic"
    Image.new("RGB", (48, 32), (90, 40, 180)).save(src, format="HEIF")
    original = src.read_bytes()
    result = convert_one(src, tmp_path / "heic_out", "JPEG", quality=95)
    assert result.success
    assert result.destination is not None
    assert result.destination.suffix == ".jpg"
    assert src.read_bytes() == original


def test_cancel_flag(sample_images: list[Path], tmp_path: Path) -> None:
    calls = {"n": 0}

    def cancel() -> bool:
        calls["n"] += 1
        return calls["n"] > 1

    summary = convert_many(
        sample_images,
        tmp_path / "cancel",
        "PNG",
        cancel_flag=cancel,
    )
    assert summary.succeeded >= 1
    assert summary.skipped >= 1
