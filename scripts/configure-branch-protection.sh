#!/usr/bin/env bash
set -euo pipefail

REPO="${1:-iamrichmack111/lyricvid-cli}"
BRANCH="${2:-main}"

echo "Configuring protection for ${REPO}:${BRANCH}"

gh api --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Validate repository",
      "Security checks",
      "Container validation",
      "Trivy filesystem"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
JSON

echo "Protection request submitted. Verify required check names in GitHub Settings if a check has not run yet."
