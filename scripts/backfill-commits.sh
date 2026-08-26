#!/usr/bin/env bash
set -euo pipefail

# Create a truthful, present-day logical commit series from an uncommitted v0.9.0
# overlay. This does NOT forge historical timestamps or authorship.
git rev-parse --is-inside-work-tree >/dev/null

commit_paths() {
  local message="$1"; shift
  local existing=()
  for path in "$@"; do [[ -e "$path" ]] && existing+=("$path"); done
  ((${#existing[@]})) || return 0
  git add -- "${existing[@]}"
  if ! git diff --cached --quiet; then
    git commit -m "$message"
  fi
}

commit_paths "security: add credential and dependency validation" \
  scripts/validate-no-secrets.sh .github/workflows/ci.yml .gitignore SECURITY.md
commit_paths "build: add production container packaging" \
  Dockerfile .dockerignore .github/workflows/container.yml
commit_paths "docs: expand README and secure YouTube workflows" \
  README.md docs/lyricvid.1 docs/architecture.d2 scripts/capture-readme-frames.mjs scripts/render-docs.sh examples
commit_paths "chore: add issue and history backfill tooling" \
  scripts/backfill-issues.sh scripts/backfill-commits.sh scripts/update-github-metadata.sh scripts/tag-release.sh
commit_paths "release: prepare LyricVid v0.9.0" \
  pyproject.toml src/lyricvid/__init__.py CHANGELOG.md .github/workflows/release.yml install.sh

if ! git diff --quiet || [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
  echo "WARNING: uncommitted files remain:" >&2
  git status --short >&2
else
  echo "✓ Logical backfill commit series complete (using current timestamps)"
fi
