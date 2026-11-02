"""Image conversion engine with quality preservation and EXIF handling."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from PIL import Image, ImageOps, UnidentifiedImageError

from photo_converter.formats import (
    INPUT_EXTENSIONS,
    LOSSLESS_FORMATS,
    NO_ALPHA_FORMATS,
    pillow_format_and_ext,
)

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], None]

# Register HEIF/AVIF openers when available.
_HEIF_AVAILABLE = False
try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
    _HEIF_AVAILABLE = True
except ImportError:
    logger.warning("pillow-heif is not installed; HEIC/HEIF/AVIF may be unavailable")


@dataclass
class ConversionResult:
    source: Path
    destination: Path | None = None
    success: bool = False
    error: str | None = None


@dataclass
class ConversionSummary:
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    results: list[ConversionResult] = field(default_factory=list)


def heif_available() -> bool:
    return _HEIF_AVAILABLE


def collect_images(paths: list[Path]) -> list[Path]:
    """Expand files/dirs into a sorted unique list of supported image files."""
    found: set[Path] = set()
    for path in paths:
        path = path.expanduser().resolve()
        if path.is_file() and path.suffix.lower() in INPUT_EXTENSIONS:
            found.add(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in INPUT_EXTENSIONS:
                    found.add(child)
    return sorted(found)


def _flatten_alpha(image: Image.Image, background: tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    """Composite transparent pixels onto an opaque background."""
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (*background, 255))
        composited = Image.alpha_composite(bg, rgba)
        return composited.convert("RGB")
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def _prepare_for_format(image: Image.Image, pillow_format: str) -> Image.Image:
    image = ImageOps.exif_transpose(image)

    if pillow_format in NO_ALPHA_FORMATS:
        return _flatten_alpha(image)

    if pillow_format == "GIF":
        # GIF palette conversion; preserve animation is out of scope for still export.
        if image.mode not in ("P", "L"):
            return image.convert("P", palette=Image.Palette.ADAPTIVE)
        return image

    if pillow_format == "ICO":
        if image.mode not in ("RGBA", "RGB"):
            return image.convert("RGBA")
        return image

    # Keep alpha when supported.
    if image.mode in ("RGBA", "LA", "P"):
        if pillow_format in ("PNG", "WEBP", "TIFF", "AVIF"):
            if image.mode == "P" and "transparency" in image.info:
                return image.convert("RGBA")
            if image.mode == "P":
                return image.convert("RGBA")
            return image
    if image.mode not in ("RGB", "RGBA", "L", "LA", "I;16"):
        return image.convert("RGB")
    return image


def _save_kwargs(pillow_format: str, quality: int) -> dict:
    """Build Pillow save() kwargs prioritizing quality / lossless where possible."""
    kwargs: dict = {}

    if pillow_format == "JPEG":
        # Near-lossless JPEG; 95 is a practical max before diminishing returns.
        q = max(1, min(100, quality))
        kwargs.update(
            {
                "quality": q,
                "subsampling": 0,  # 4:4:4 — no chroma subsampling
                "optimize": True,
            }
        )
    elif pillow_format == "PNG":
        kwargs.update({"compress_level": 6, "optimize": True})
    elif pillow_format == "WEBP":
        if quality >= 100:
            kwargs.update({"lossless": True, "quality": 100, "method": 6})
        else:
            kwargs.update({"quality": quality, "method": 6})
    elif pillow_format == "TIFF":
        kwargs.update({"compression": "tiff_lzw"})
    elif pillow_format == "AVIF":
        if quality >= 100:
            kwargs.update({"quality": 100})
        else:
            kwargs.update({"quality": quality})
    elif pillow_format == "ICO":
        kwargs.update({"sizes": [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]})

    return kwargs


def convert_one(
    source: Path,
    destination_dir: Path,
    output_label: str,
    *,
    quality: int = 95,
    overwrite: bool = False,
) -> ConversionResult:
    """Convert a single image. Original file is never modified."""
    source = source.expanduser().resolve()
    destination_dir = destination_dir.expanduser().resolve()

    result = ConversionResult(source=source)

    try:
        pillow_format, ext = pillow_format_and_ext(output_label)
        destination_dir.mkdir(parents=True, exist_ok=True)
        dest = destination_dir / f"{source.stem}{ext}"

        if dest.exists() and not overwrite:
            # Avoid clobbering: append numeric suffix.
            counter = 1
            while True:
                candidate = destination_dir / f"{source.stem}_{counter}{ext}"
                if not candidate.exists():
                    dest = candidate
                    break
                counter += 1

        with Image.open(source) as img:
            prepared = _prepare_for_format(img, pillow_format)
            exif = img.info.get("exif")
            icc = img.info.get("icc_profile")

            save_kwargs = _save_kwargs(pillow_format, quality)
            if exif and pillow_format in ("JPEG", "WEBP", "TIFF"):
                save_kwargs["exif"] = exif
            if icc and pillow_format in ("JPEG", "PNG", "WEBP", "TIFF"):
                save_kwargs["icc_profile"] = icc

            prepared.save(dest, format=pillow_format, **save_kwargs)

        result.destination = dest
        result.success = True
        logger.info("Converted %s → %s", source, dest)
    except UnidentifiedImageError:
        result.error = f"Unrecognized or corrupted image: {source.name}"
        logger.exception(result.error)
    except OSError as exc:
        result.error = f"I/O error for {source.name}: {exc}"
        logger.exception(result.error)
    except Exception as exc:  # noqa: BLE001 — surface any conversion failure to UI
        result.error = f"Failed to convert {source.name}: {exc}"
        logger.exception(result.error)

    return result


def convert_many(
    sources: list[Path],
    destination_dir: Path,
    output_label: str,
    *,
    quality: int = 95,
    overwrite: bool = False,
    progress: ProgressCallback | None = None,
    cancel_flag: Callable[[], bool] | None = None,
) -> ConversionSummary:
    """Convert multiple images with optional progress reporting."""
    summary = ConversionSummary(total=len(sources))

    for index, source in enumerate(sources, start=1):
        if cancel_flag and cancel_flag():
            summary.skipped += summary.total - (index - 1)
            break

        if progress:
            progress(index, summary.total, source.name)

        item = convert_one(
            source,
            destination_dir,
            output_label,
            quality=quality,
            overwrite=overwrite,
        )
        summary.results.append(item)
        if item.success:
            summary.succeeded += 1
        else:
            summary.failed += 1

    return summary


def format_quality_hint(output_label: str) -> str:
    pillow_format, _ = pillow_format_and_ext(output_label)
    if pillow_format in LOSSLESS_FORMATS:
        return "Lossless format — original pixel data preserved."
    if pillow_format == "WEBP":
        return "WEBP at quality 100 uses lossless mode."
    if pillow_format == "JPEG":
        return "JPEG uses high quality (95) and 4:4:4 chroma (minimal loss)."
    if pillow_format == "AVIF":
        return "AVIF at quality 100 aims for near-lossless compression."
    return "Best-effort quality preservation."
