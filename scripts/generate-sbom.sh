#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-dist}"
mkdir -p "$OUT"
python -m pip install --quiet --disable-pip-version-check cyclonedx-bom
cyclonedx-py environment --output-format JSON --output-file "$OUT/lyricvid-python.cdx.json"
python - <<'PY'
import json, pathlib
p = pathlib.Path('dist/lyricvid-python.cdx.json')
if p.exists():
    data = json.loads(p.read_text())
    print(f"SBOM components: {len(data.get('components', []))}")
PY
