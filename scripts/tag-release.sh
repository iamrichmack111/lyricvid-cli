#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v git >/dev/null 2>&1 || { echo "ERROR: git is required"; exit 1; }

VERSION="$(python3 - <<'PY'
import re
from pathlib import Path
text = Path('pyproject.toml').read_text(encoding='utf-8')
m = re.search(r'^version = "([^"]+)"', text, re.M)
if not m:
    raise SystemExit('Could not read project version')
print(m.group(1))
PY
)"
TAG="v$VERSION"

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: Working tree is not clean. Commit the release changes first."
  git status --short
  exit 1
fi

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "ERROR: Tag already exists: $TAG"
  exit 1
fi

BRANCH="$(git branch --show-current)"
[ -n "$BRANCH" ] || { echo "ERROR: Detached HEAD; checkout a branch first."; exit 1; }

echo "Creating annotated tag $TAG on $BRANCH..."
git tag -a "$TAG" -m "LyricVid $VERSION"

echo "Pushing branch and tag to origin..."
git push origin "$BRANCH"
git push origin "$TAG"

echo "✓ Pushed $TAG"
echo "The GitHub Release workflow should create the release automatically."
