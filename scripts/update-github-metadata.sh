#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-iamrichmack111/lyricvid-cli}"
command -v gh >/dev/null 2>&1 || { echo "ERROR: GitHub CLI (gh) is required." >&2; exit 1; }
gh auth status >/dev/null

gh repo edit "$REPO" \
  --description "Whisper-aligned Remotion lyric videos, visualizers, voice-over, detached rendering, secure YouTube publishing, and GHCR packaging from the terminal." \
  --add-topic remotion \
  --add-topic faster-whisper \
  --add-topic ffmpeg \
  --add-topic lyric-video \
  --add-topic video-generation \
  --add-topic youtube-api \
  --add-topic oauth \
  --add-topic python-cli \
  --add-topic karaoke \
  --add-topic speech-to-text \
  --add-topic music-visualizer \
  --add-topic content-automation \
  --add-topic playwright \
  --add-topic d2 \
  --add-topic ghcr

echo "✓ Updated GitHub description and topics for $REPO"
