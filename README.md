# photo-converter

Open-source **Photo Converter** — batch-convert photos (JPEG, HEIC, PNG, …) to a chosen format without modifying originals.

**Repository:** [https://github.com/ZRR1498/photo-converter](https://github.com/ZRR1498/photo-converter)  
**License:** [MIT](LICENSE) · Copyright (c) 2026 ZRR1498

All application code lives in [`main-app/`](main-app/).

```bash
cd main-app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

See **[main-app/README.md](main-app/README.md)** for full docs: quality policy, UI (EN/RU), explorer file picker, tests, PyInstaller builds for Linux / Windows / macOS.

### Third-party (runtime)

This project depends on open-source libraries (Pillow, pillow-heif, CustomTkinter, darkdetect). Their licenses remain with their authors; see each package for details. PyInstaller is used only as an optional build tool.
