# Photo Converter

**Open-source** cross-platform desktop app that batch-converts photos to a chosen format — without touching the originals.

| | |
|---|---|
| **License** | [MIT](LICENSE) |
| **Language** | Python 3.10+ |
| **OS** | Linux · Windows · macOS |
| **UI** | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| **Engine** | [Pillow](https://python-pillow.org/) + [pillow-heif](https://github.com/bigcat88/pillow_heif) |

---

## What it does

1. Click **Select photos…** or **Select folder…** — an explorer-style browser opens (Pictures by default). Multi-select photos with **Ctrl+click**, **Shift+click**, mouse drag, or **Ctrl+A**; double-click folders to navigate.
2. Choose the **output format** (JPEG, PNG, WEBP, TIFF, BMP, GIF, ICO, AVIF).
3. Optionally tune **quality** (for lossy targets) — defaults aim for minimal / no quality loss.
4. Click **Choose folder…** to pick where converted files will be saved.
5. Hit **Convert**. Progress, per-file log, cancel, and clear error dialogs are built in.

**Originals are never modified.** Converted files keep the same base name with a new extension (e.g. `vacation.HEIC` → `vacation.jpg`). If a name already exists, a numeric suffix is added unless overwrite is enabled.

**Language:** switch **English / Русский** in the top-right of the window (defaults from the OS locale).

---

## Quality policy

| Target | Behavior |
|--------|----------|
| **PNG / TIFF / BMP** | Lossless |
| **WEBP @ 100** | Lossless WEBP |
| **JPEG** | Quality **95**, `optimize`, chroma **4:4:4** (no subsampling) — near-lossless for photos |
| **AVIF** | High quality (100 when slider is max) |
| **Alpha → JPEG/BMP** | Transparent pixels flattened onto white (required by those formats) |
| **EXIF / ICC** | Preserved when the target format supports them |

---

## Requirements

- **Python 3.10+**
- Tk / Tcl (usually bundled with Python on Windows/macOS; on Linux install `python3-tk`)
- For **HEIC/HEIF/AVIF**: `pillow-heif` (pulled in via `requirements.txt`). On some Linux distros you may also need system `libheif`:

```bash
# Debian / Ubuntu
sudo apt install python3-tk libheif1

# Fedora
sudo dnf install python3-tkinter libheif
```

---

## Install (development)

```bash
cd main-app
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_icon.py    # creates assets/icon.png + icon.ico
```

---

## Run

```bash
# from main-app/
python run.py
# or
python -m photo_converter
```

---

## Tests

```bash
cd main-app
pytest -q
```

Tests cover collection, JPEG↔PNG conversion, alpha flattening, overwrite / collision naming, cancel, and corrupt-file errors. Originals are asserted unchanged after conversion.

---

## Build standalone app (current OS)

Builds a single binary with **PyInstaller** and the app icon.

### Linux / macOS

```bash
cd main-app
chmod +x scripts/build.sh
./scripts/build.sh
```

Output: `dist/PhotoConverter`.

> On Linux the window icon still loads from the bundled PNG at runtime; embedding an `.ico` into the ELF binary is a Windows/macOS PyInstaller feature.

### Windows

```bat
cd main-app
scripts\build.bat
```

Output: `dist\PhotoConverter.exe`

> Build on the OS you target: Linux binary on Linux, `.exe` on Windows, macOS app on macOS.

---

## Project layout

```
main-app/
├── photo_converter/       # Application package
│   ├── app.py             # GUI
│   ├── converter.py       # Conversion engine
│   ├── formats.py         # Supported formats
│   └── __main__.py
├── assets/                # icon.png / icon.ico
├── scripts/
│   ├── build.sh / build.bat
│   └── generate_icon.py
├── tests/
├── run.py                 # Dev entrypoint
├── photo_converter.spec   # PyInstaller spec
├── requirements.txt
├── pyproject.toml
├── LICENSE                # MIT
└── README.md
```

---

## Supported formats

**Input (read):** JPG/JPEG, PNG, BMP, GIF, TIFF, WEBP, HEIC/HEIF, AVIF, ICO, PPM/PGM/PBM, TGA, JPEG 2000  

**Output (write):** JPEG, PNG, WEBP, TIFF, BMP, GIF, ICO, AVIF  

Availability of HEIC/AVIF depends on `pillow-heif` and system codecs; the UI shows whether HEIF support is enabled.

---

## Contributing

Issues and pull requests are welcome. Please keep the MIT license header spirit: free to use, modify, and redistribute.

```bash
# typical contribution loop
pip install -r requirements.txt
pytest -q
```

---

## License

Released under the **MIT License** — see [LICENSE](LICENSE). Free and open source software.
