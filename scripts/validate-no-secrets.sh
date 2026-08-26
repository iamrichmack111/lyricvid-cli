#!/usr/bin/env bash
set -euo pipefail

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
  mapfile -t FILES < <(git ls-files)
else
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  mapfile -t FILES < <(cd "$ROOT" && find . -type f \
    -not -path './.git/*' -not -path './.venv/*' -not -path './node_modules/*' \
    -not -path './build/*' -not -path './dist/*' | sed 's#^./##')
fi
cd "$ROOT"

fail=0

for path in "${FILES[@]}"; do
  case "$path" in
    .secrets/*|*/.secrets/*|youtube-oauth.json|*/youtube-oauth.json|youtube-token.json|*/youtube-token.json|client_secret_*.json|*/client_secret_*.json|credentials.json|*/credentials.json)
      echo "ERROR: sensitive credential path is included/tracked: $path" >&2
      fail=1
      ;;
  esac
done

PATTERNS=(
  '-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'
  '"client_secret"[[:space:]]*:[[:space:]]*"[^"$<{][^"]{8,}"'
  'AIza[0-9A-Za-z_-]{30,}'
  'gh[pousr]_[0-9A-Za-z]{20,}'
  'github_pat_[0-9A-Za-z_]{20,}'
  'sk-[A-Za-z0-9_-]{20,}'
  'AKIA[0-9A-Z]{16}'
)

for path in "${FILES[@]}"; do
  [[ -f "$path" ]] || continue
  case "$path" in
    scripts/validate-no-secrets.sh|README.md|docs/lyricvid.1) continue ;;
  esac
  # Skip obvious binary/media payloads.
  if ! grep -Iq . "$path" 2>/dev/null; then continue; fi
  for pattern in "${PATTERNS[@]}"; do
    if grep -nE "$pattern" "$path" >/tmp/lyricvid-secret-scan.$$ 2>/dev/null; then
      echo "ERROR: possible credential material found in $path:" >&2
      cat /tmp/lyricvid-secret-scan.$$ >&2
      fail=1
    fi
  done
done
rm -f /tmp/lyricvid-secret-scan.$$

if (( fail )); then
  echo "Secret validation failed. Remove/rotate credentials and clean Git history before pushing." >&2
  exit 1
fi

echo "✓ No OAuth/token files or high-confidence credential strings detected"
