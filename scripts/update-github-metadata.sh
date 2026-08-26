#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-iamrichmack111/lyricvid-cli-new}"
if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI (gh) is required." >&2
  exit 1
fi

gh repo edit "$REPO" \
  --description "Whisper-aligned Remotion lyric videos, music visualizers, voice-over compositions, detached rendering, and YouTube publishing from the terminal." \
  --add-topic remotion \
  --add-topic faster-whisper \
  --add-topic ffmpeg \
  --add-topic lyric-video \
  --add-topic video-generation \
  --add-topic youtube-api \
  --add-topic python-cli \
  --add-topic karaoke \
  --add-topic speech-to-text \
  --add-topic music-visualizer \
  --add-topic content-automation \
  --add-topic playwright \
  --add-topic d2

echo "✓ Updated GitHub description and topics for $REPO"
