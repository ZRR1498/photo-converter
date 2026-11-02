"""Supported input/output image formats."""

from __future__ import annotations

# Extensions the converter can read (case-insensitive).
INPUT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".gif",
        ".tiff",
        ".tif",
        ".webp",
        ".heic",
        ".heif",
        ".avif",
        ".ico",
        ".ppm",
        ".pgm",
        ".pbm",
        ".tga",
        ".jp2",
        ".j2k",
        ".jpf",
        ".jpx",
    }
)

# User-facing output format choices → Pillow save format + preferred extension.
OUTPUT_FORMATS: dict[str, tuple[str, str]] = {
    "JPEG": ("JPEG", ".jpg"),
    "PNG": ("PNG", ".png"),
    "WEBP": ("WEBP", ".webp"),
    "TIFF": ("TIFF", ".tiff"),
    "BMP": ("BMP", ".bmp"),
    "GIF": ("GIF", ".gif"),
    "ICO": ("ICO", ".ico"),
    "AVIF": ("AVIF", ".avif"),
}

OUTPUT_FORMAT_LABELS: tuple[str, ...] = tuple(OUTPUT_FORMATS.keys())

# Formats that do not support alpha; RGBA must be flattened first.
NO_ALPHA_FORMATS: frozenset[str] = frozenset({"JPEG", "BMP"})

# Formats that are inherently lossless (or can be saved losslessly).
LOSSLESS_FORMATS: frozenset[str] = frozenset({"PNG", "TIFF", "BMP", "GIF"})


def is_supported_input(path_suffix: str) -> bool:
    return path_suffix.lower() in INPUT_EXTENSIONS


def pillow_format_and_ext(label: str) -> tuple[str, str]:
    if label not in OUTPUT_FORMATS:
        raise ValueError(f"Unsupported output format: {label}")
    return OUTPUT_FORMATS[label]
