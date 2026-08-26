#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="lyricvid"

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

# Resolve pipx paths from pipx itself when possible. These fallbacks match the
# normal macOS/Linux user install paths.
PIPX_HOME="$($PIPX environment --value PIPX_HOME 2>/dev/null || true)"
PIPX_BIN_DIR="$($PIPX environment --value PIPX_BIN_DIR 2>/dev/null || true)"
PIPX_HOME="${PIPX_HOME:-$HOME/.local/pipx}"
PIPX_BIN_DIR="${PIPX_BIN_DIR:-$HOME/.local/bin}"
APP_VENV="$PIPX_HOME/venvs/$APP"
APP_BIN="$PIPX_BIN_DIR/$APP"

# pipx can be configured to use uv. uv intentionally refuses to create a venv
# over an existing directory unless UV_VENV_CLEAR=1 is set. Uninstall first,
# clean only LyricVid's stale app-specific paths, then explicitly permit uv to
# replace the venv if pipx still sees a race/stale directory.
if [ -e "$APP_VENV" ] || [ -e "$APP_BIN" ] || "$PIPX" list 2>/dev/null | grep -qi "package $APP"; then
  echo "Replacing existing LyricVid pipx installation..."
  "$PIPX" uninstall "$APP" >/dev/null 2>&1 || true
fi

if [ -d "$APP_VENV" ]; then
  echo "Removing stale LyricVid environment: $APP_VENV"
  rm -rf "$APP_VENV"
fi
rm -f "$APP_BIN"

# The uv hint itself recommends UV_VENV_CLEAR=1. Scope it to this installation
# command so it cannot affect unrelated virtual environments.
echo "Installing LyricVid from: $ROOT"
UV_VENV_CLEAR=1 "$PIPX" install "$ROOT" --force
"$PIPX" ensurepath >/dev/null 2>&1 || true

# Install the bundled man page into the per-user man tree. This avoids sudo
# and lets standard `man lyricvid` discovery work on systems that include the
# user manpath. The source file remains available under docs/ as a fallback.
MAN_DIR="$HOME/.local/share/man/man1"
mkdir -p "$MAN_DIR"
install -m 0644 "$ROOT/docs/lyricvid.1" "$MAN_DIR/lyricvid.1"
echo "Installed man page: $MAN_DIR/lyricvid.1"

# Architecture docs are source-controlled as D2. Render the SVG automatically
# when D2 is already present, but never make D2 a hard installation dependency.
if command -v d2 >/dev/null 2>&1; then
  if "$ROOT/scripts/render-docs.sh"; then
    echo "Architecture diagram rendered."
  else
    echo "WARNING: D2 is installed but architecture rendering failed." >&2
  fi
else
  echo "D2 not found; skipping architecture.svg render (source remains in docs/architecture.d2)."
fi

echo
echo "LyricVid installed successfully."
if command -v lyricvid >/dev/null 2>&1; then
  lyricvid --version || true
else
  echo "Open a new shell if 'lyricvid' is not immediately on PATH."
fi

echo
echo "Examples:"
echo "  lyricvid --doctor"
echo "  lyricvid styles"
echo "  cd /path/to/music && lyricvid ."
echo "  lyricvid /path/to/music"
echo
echo "Manual:"
echo "  man lyricvid"
echo "  # fallback: man $ROOT/docs/lyricvid.1"
