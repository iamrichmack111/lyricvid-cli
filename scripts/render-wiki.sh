#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v d2 >/dev/null || {
  echo "ERROR: d2 is required. On macOS: brew install d2" >&2
  exit 1
}

mkdir -p wiki/diagrams
count=0
failed=0

for src in wiki/diagrams/*.d2; do
  [ -e "$src" ] || continue
  out="${src%.d2}.svg"
  echo "Rendering $src -> $out"
  if d2 --layout=elk --bundle=true "$src" "$out"; then
    count=$((count + 1))
  else
    echo "ERROR: failed to render $src" >&2
    failed=$((failed + 1))
  fi
done

if [ "$failed" -ne 0 ]; then
  echo "✗ $failed diagram(s) failed; $count rendered successfully" >&2
  exit 1
fi

echo "✓ Rendered $count wiki diagrams using vendored local icons"
