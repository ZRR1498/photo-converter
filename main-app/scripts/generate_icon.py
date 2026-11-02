#!/usr/bin/env python3
"""Generate app icons (PNG + ICO) with Pillow — no external design tools required."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


def make_icon(size: int = 512) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = size // 16
    # Soft rounded square background
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 6,
        fill=(24, 119, 210, 255),
    )

    # Stylized photo frame
    frame = [
        size * 0.22,
        size * 0.28,
        size * 0.78,
        size * 0.72,
    ]
    draw.rounded_rectangle(frame, radius=size // 20, fill=(255, 255, 255, 235))

    # Landscape mountain silhouette
    mountain = [
        (size * 0.28, size * 0.62),
        (size * 0.42, size * 0.42),
        (size * 0.52, size * 0.54),
        (size * 0.62, size * 0.38),
        (size * 0.72, size * 0.62),
    ]
    draw.polygon(mountain, fill=(24, 119, 210, 220))

    # Sun
    r = size * 0.05
    cx, cy = size * 0.64, size * 0.38
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 196, 72, 255))

    # Small arrow hint (convert)
    tip_x = size * 0.78
    tip_y = size * 0.78
    draw.polygon(
        [
            (tip_x - size * 0.08, tip_y - size * 0.02),
            (tip_x, tip_y - size * 0.08),
            (tip_x + size * 0.02, tip_y + size * 0.02),
        ],
        fill=(255, 255, 255, 255),
    )

    return img


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    master = make_icon(512)
    png_path = assets / "icon.png"
    master.save(png_path, format="PNG")

    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_images = [master.resize(s, Image.Resampling.LANCZOS) for s in ico_sizes]
    ico_path = assets / "icon.ico"
    ico_images[-1].save(ico_path, format="ICO", sizes=ico_sizes)

    print(f"Wrote {png_path}")
    print(f"Wrote {ico_path}")


if __name__ == "__main__":
    main()
