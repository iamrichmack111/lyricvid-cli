#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3.10+ is required."
  exit 1
fi

if command -v pipx >/dev/null 2>&1; then
  PIPX="$(command -v pipx)"
else
  echo "pipx was not found; bootstrapping a private copy..."
  BOOT="$HOME/.local/share/lyricvid-pipx-bootstrap"
  rm -rf "$BOOT"
  python3 -m venv "$BOOT"
  "$BOOT/bin/python" -m pip install -U pip pipx
  PIPX="$BOOT/bin/pipx"
fi

"$PIPX" install --force "$ROOT"
"$PIPX" ensurepath || true

echo
echo "LyricVid installed."
echo "Open a new shell if 'lyricvid' is not immediately on PATH."
echo
echo "Examples:"
echo "  lyricvid --doctor"
echo "  cd /path/to/music && lyricvid ."
echo "  lyricvid /path/to/music"
