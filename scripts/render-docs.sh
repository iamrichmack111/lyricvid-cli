#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v d2 >/dev/null 2>&1; then
  echo "ERROR: d2 is required. Install D2, then rerun this script." >&2
  exit 1
fi
mkdir -p "$ROOT/docs"
d2 --layout=elk --theme=200 "$ROOT/docs/architecture.d2" "$ROOT/docs/architecture.svg"
echo "✓ Rendered docs/architecture.svg"
