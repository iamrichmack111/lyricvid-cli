#!/usr/bin/env bash
set -euo pipefail

command -v gh >/dev/null || { echo "ERROR: gh is required" >&2; exit 1; }
gh auth status >/dev/null
repo="${1:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"

create_closed_issue() {
  local title="$1" body="$2" labels="$3"
  local existing
  existing="$(gh issue list -R "$repo" --state all --search "in:title \"$title\"" --json number,title --jq ".[] | select(.title == \"$title\") | .number" | head -1)"
  if [[ -n "$existing" ]]; then
    echo "exists #$existing: $title"
    return
  fi
  local args=(issue create -R "$repo" --title "$title" --body "$body")
  if [[ -n "$labels" ]]; then args+=(--label "$labels"); fi
  local url number
  url="$(gh "${args[@]}")"
  number="${url##*/}"
  gh issue close -R "$repo" "$number" --reason completed --comment "Backfilled as completed work represented in the v0.9.0 codebase and release history."
  echo "closed #$number: $title"
}

# Create labels opportunistically; ignore if already present.
for spec in \
  'feature:0E8A16:Completed product capability' \
  'docs:1D76DB:Documentation and examples' \
  'security:D73A4A:Security and validation' \
  'ci-cd:5319E7:Continuous integration and delivery' \
  'youtube:FF0000:YouTube publishing integration' \
  'video:8A2BE2:Rendering and video composition'; do
  IFS=: read -r name color desc <<<"$spec"
  gh label create -R "$repo" "$name" --color "$color" --description "$desc" --force >/dev/null 2>&1 || true
done

create_closed_issue "Preserve authored lyrics and align with Whisper timing" "Use embedded/sidecar authored lyrics as display text while faster-whisper supplies acoustic timing anchors." "feature,video"
create_closed_issue "Probe media metadata with ffprobe and Mutagen" "Inspect container and tag metadata for lyrics and media properties before transcription/rendering." "feature,video"
create_closed_issue "Add Remotion visual presets and social formats" "Provide reusable visual presets plus landscape, vertical short, and square output formats." "feature,video"
create_closed_issue "Add PNG artwork, motion backgrounds, and voice-over" "Support album artwork modes, looping background video, narration tracks, and independent audio levels." "feature,video"
create_closed_issue "Add detached rendering and job status" "Allow long renders/uploads to survive terminal loss and expose logs/job status." "feature,video"
create_closed_issue "Add YouTube OAuth upload workflow" "Publish rendered MP4s through YouTube Data API v3 with privacy, tags, descriptions, and resumable uploads." "feature,youtube"
create_closed_issue "Support description files and upload dry runs" "Load YouTube descriptions from Markdown/text sidecars and validate metadata without uploading." "feature,youtube"
create_closed_issue "Add branded intro, outro, artist metadata, and section labels" "Add Richmack Radio branding, cover-art intro/outro, artist display, and Verse/Chorus/Bridge labels." "feature,video"
create_closed_issue "Reduce between-line lyric flashing" "Use conservative non-overlapping lyric windows and suppress extremely short inferred spans." "feature,video"
create_closed_issue "Add metro-cinematic visual preset" "Add a restrained neon/metro music-video treatment distinct from the HUD-heavy presets." "feature,video"
create_closed_issue "Add Playwright README frame capture" "Capture deterministic intro, midpoint, and outro frames from rendered videos for repository documentation." "docs,video"
create_closed_issue "Add D2 architecture documentation" "Maintain the rendering/publishing architecture as D2 source and render it to SVG." "docs"
create_closed_issue "Add detailed Unix man page" "Document commands, lyric policy, rendering, jobs, YouTube upload, security, and troubleshooting in manpage form." "docs"
create_closed_issue "Harden pipx installer and install man page" "Handle stale pipx/uv environments and install the LyricVid man page into the local man path." "feature"
create_closed_issue "Add CI validation and dependency security checks" "Validate versions, shell scripts, D2, credentials, Python dependencies, static security, tests, packages, and container builds." "security,ci-cd"
create_closed_issue "Publish a GHCR container image with provenance" "Build and publish the LyricVid image to GHCR with version/SHA tags and artifact provenance attestations." "security,ci-cd"
create_closed_issue "Expand README with secure YouTube production workflows" "Document installation, project layout, render QA, OAuth handling, upload workflows, detached operation, container usage, and troubleshooting." "docs,youtube"

create_closed_issue "Add Dependabot dependency update automation" "Configured Dependabot for Python, Remotion npm, Docker, and GitHub Actions dependencies." "security,ci-cd"
create_closed_issue "Add CodeQL static analysis" "Added CodeQL scanning for Python and JavaScript/TypeScript with security-extended queries." "security,ci-cd"
create_closed_issue "Add Trivy and dependency review security gates" "Added Trivy filesystem scanning and pull-request dependency review for vulnerable dependencies and selected licenses." "security,ci-cd"
create_closed_issue "Add OpenSSF Scorecard supply-chain analysis" "Added scheduled OpenSSF Scorecard analysis with SARIF upload." "security,ci-cd"
create_closed_issue "Add real integration render smoke test" "Added scheduled/manual end-to-end rendering of a small media fixture followed by ffprobe codec, resolution, and audio validation." "ci-cd,video"
create_closed_issue "Add release SBOM generation" "Added CycloneDX SBOM generation to tagged release assets." "security,ci-cd"
create_closed_issue "Add repository contribution and governance controls" "Added CODEOWNERS, pull request template, issue forms, CONTRIBUTING.md, pre-commit hooks, and branch-protection configuration helper." "docs,security"

echo "✓ Backfilled completed issues in $repo"
