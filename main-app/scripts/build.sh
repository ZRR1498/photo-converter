#!/usr/bin/env bash
# Build a standalone PhotoConverter binary for the current OS (Linux / macOS).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"

echo "==> Ensuring dependencies…"
"$PYTHON" -m pip install -r requirements.txt

echo "==> Generating icons…"
"$PYTHON" scripts/generate_icon.py

echo "==> Cleaning previous build artifacts…"
rm -rf build dist

echo "==> Running PyInstaller…"
"$PYTHON" -m PyInstaller --noconfirm photo_converter.spec

OS="$(uname -s)"
echo
echo "Build complete for ${OS}."
if [[ -d dist ]]; then
  ls -lah dist
fi
echo
echo "Run the binary from ./dist/PhotoConverter (on Windows: PhotoConverter.exe)."
