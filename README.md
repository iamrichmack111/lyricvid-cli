# LyricVid

[![CI](https://github.com/iamrichmack111/lyricvid-cli-new/actions/workflows/ci.yml/badge.svg)](https://github.com/iamrichmack111/lyricvid-cli-new/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/iamrichmack111/lyricvid-cli-new?display_name=tag)](https://github.com/iamrichmack111/lyricvid-cli-new/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Remotion](https://img.shields.io/badge/Remotion-4.x-6C63FF)](https://www.remotion.dev/)
[![faster-whisper](https://img.shields.io/badge/Whisper-faster--whisper-orange)](https://github.com/SYSTRAN/faster-whisper)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-007808)](https://ffmpeg.org/)
[![YouTube API](https://img.shields.io/badge/YouTube-Data%20API%20v3-FF0000)](https://developers.google.com/youtube/v3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**LyricVid is a terminal-driven Remotion video engine for Whisper-aligned lyric videos, album-art visualizers, narrated explainers, Shorts/Reels variants, detached rendering, and OAuth-based YouTube publishing.**

Instead of trusting speech recognition to rewrite your lyrics, LyricVid can preserve authored text from embedded metadata or sidecar files and use **faster-whisper as the acoustic timing layer**. ffprobe, Mutagen, sequence alignment, Remotion, FFmpeg, artwork, voice-over, and YouTube publishing are combined into one reproducible CLI workflow.

## Preview

After rendering a sample video, generate README frames with Playwright:

```bash
npm install --save-dev playwright
npx playwright install chromium
node scripts/capture-readme-frames.mjs ./lyric-videos/your-video.mp4
```

| Intro | Mid-song lyric scene |
| --- | --- |
| ![LyricVid intro](docs/screenshots/intro.png) | ![LyricVid middle](docs/screenshots/middle.png) |

The capture script also writes `docs/screenshots/outro.png` for outro documentation.

## Why LyricVid

- **Exact authored lyrics first.** ffprobe/embedded metadata and lyric sidecars can remain the displayed source of truth.
- **Whisper for timing.** faster-whisper listens to the performed vocal and supplies acoustic anchors.
- **Conservative lyric windows.** Non-overlapping line windows reduce brief between-line flashes; section markers such as `[Verse 1]` are treated as labels.
- **Real Remotion composition.** Artwork intros, animated lyric scenes, looping backgrounds, voice-over, multiple layouts, presets, and outros.
- **Multiple social formats.** Landscape YouTube, vertical Shorts/Reels/TikTok, and square output.
- **Detached execution.** Long Whisper + Remotion jobs can survive terminal closure or an SSH disconnect.
- **YouTube publishing.** OAuth 2.0, Markdown/text descriptions, tags, privacy controls, resumable uploads, and dry runs.
- **Documentation as code.** D2 architecture source, Playwright screenshot automation, a full Unix man page, and CI/CD.

## Architecture

The source-of-truth diagram is [`docs/architecture.d2`](docs/architecture.d2). Render it with:

```bash
./scripts/render-docs.sh
```

That produces `docs/architecture.svg` when D2 is installed.

```text
Audio / artwork / narration
          │
          ├── ffprobe + Mutagen + sidecars
          ├── faster-whisper acoustic timing
          │              │
          │      exact-text alignment
          │              │
          └──────────► Remotion
                         │
              intro → lyrics → outro
                         │
                       FFmpeg
                         │
              detached job / YouTube API
```

## Install

Clone and install with pipx:

```bash
git clone git@github.com:iamrichmack111/lyricvid-cli-new.git
cd lyricvid-cli-new
./install.sh
```

Verify the stack:

```bash
lyricvid --version
lyricvid styles
lyricvid --doctor
```

The installer exposes `lyricvid` on your PATH while keeping Python dependencies isolated.

### Man page

A detailed manual is included at `docs/lyricvid.1`.

```bash
man ./docs/lyricvid.1
```

On systems where local man directories are indexed, you can also copy it into a man1 directory and use `man lyricvid`.

## Quick start

Render every supported audio file in the current folder:

```bash
lyricvid .
```

Render a single-song folder with album artwork and a preset:

```bash
lyricvid . \
  --style metro-cinematic \
  --image cover.png \
  --artist "Esoterica" \
  --brand "Richmack Radio" \
  --intro-seconds 5 \
  --outro-seconds 7 \
  --outro-text "COMPETE FOR YOU - ESOTERICA" \
  --detach
```

Output defaults to:

```text
<source-folder>/lyric-videos/
```

## Lyric intelligence

Default `--lyrics-source auto` follows this policy:

```text
ffprobe/container lyric metadata
        ↓
embedded media lyrics (Mutagen)
        ↓
matching sidecar lyrics
        ↓
Whisper-only transcription if authored text is unavailable
```

Whisper contributes **timing**, not necessarily final spelling. If the performed audio is recognized as `T Shark` but the authored lyric says `TShark`, LyricVid can display `TShark` while aligning it against Whisper's word timings.

Supported authored sources include MP3 ID3 `USLT`/`SYLT`, M4A/MP4 `©lyr`, FLAC/Ogg/Vorbis lyric fields, and sidecars such as:

```text
Terraform.mp3
Terraform.lyrics.txt
```

Inspect lyric sources without loading Whisper:

```bash
lyricvid . --lyrics-info
```

Transcribe/align without rendering:

```bash
lyricvid . --transcribe-only
```

Force fresh acoustic timing:

```bash
lyricvid . --retranscribe --force
```

Each run can produce `lyric-videos/alignment-report.json` for QA.

## Visual styles

List the installed presets:

```bash
lyricvid styles
```

Current presets:

| Style | Best for |
| --- | --- |
| `cyberpunk` | High-energy neon lyric videos |
| `terminal-green` | CLI / hacker / terminal themes |
| `daemon-red` | Aggressive ops and infrastructure visuals |
| `root-violet` | Dark violet cinematic treatment |
| `system-amber` | Retro-computing / command-line visuals |
| `network-teal` | Cloud and networking topics |
| `neon-pink` | Social-first pop/R&B treatment |
| `minimal-clean` | Clean centered artwork and reduced effects |
| `podcast` | Narration, commentary, audio shows |
| `explainer` | Diagrams, technical narration, lessons |
| `metro-cinematic` | Album-art music video with restrained neon and metro mood |

## Artwork, intros, and outros

Use album art as the primary visual source:

```bash
lyricvid . --image cover.png --image-mode background
```

Available artwork modes:

```text
background
card
logo
```

Add an intro and outro:

```bash
lyricvid . \
  --image cover.png \
  --intro-seconds 5 \
  --outro-seconds 7 \
  --outro-text "THANKS FOR LISTENING"
```

`--outro-image` can use different artwork; otherwise the main image is reused.

## Voice-over and motion backgrounds

Narration over music:

```bash
lyricvid . \
  --style explainer \
  --voiceover narration.mp3 \
  --music-volume 0.25 \
  --voiceover-volume 1.0
```

Loop a motion background:

```bash
lyricvid . \
  --background-video terminal-loop.mp4 \
  --style cyberpunk
```

## Output formats

Landscape YouTube:

```bash
lyricvid . --format landscape
```

YouTube Shorts / Reels / TikTok:

```bash
lyricvid . --format short
```

Square:

```bash
lyricvid . --format square
```

## Detached rendering

Start a job that survives terminal closure:

```bash
lyricvid . --style metro-cinematic --detach
```

LyricVid prints the PID, job ID, log file, and an exact `tail -f` command. List recent jobs later with:

```bash
lyricvid jobs
```

Metadata and logs live under:

```text
~/.cache/lyricvid/jobs/
```

## YouTube upload

Create OAuth Desktop credentials for a Google Cloud project with **YouTube Data API v3** enabled, then keep the credentials outside Git.

Default paths relative to the current project are:

```text
.secrets/youtube-oauth.json
.secrets/youtube-token.json
```

Upload publicly with metadata from a file:

```bash
lyricvid upload ./lyric-videos/song.mp4 \
  --title "Esoterica - Compete for You | Official Lyric Video" \
  --description-file description.md \
  --tags "Esoterica,Compete for You,R&B,lyric video,Richmack Radio" \
  --public
```

Without `--public` or `--unlisted`, uploads default to **private**.

Preview metadata without uploading:

```bash
lyricvid upload ./lyric-videos/song.mp4 \
  --title "Test" \
  --description-file description.md \
  --dry-run
```

After OAuth has been established, uploads can also run detached:

```bash
lyricvid upload ./lyric-videos/song.mp4 \
  --title "Song" \
  --description-file description.md \
  --public \
  --detach
```

### Why a new upload may initially look 360p

YouTube can make the low-resolution transcode available before HD processing has completed. The original source upload is unchanged; 720p/1080p variants can appear later after YouTube finishes processing.

## Remotion Studio

Prepare the current project and open Remotion Studio:

```bash
lyricvid . --studio
```

This is useful for experimenting interactively before committing to a full render.

## Quality and performance

Use a larger Whisper model when timing/recognition needs more acoustic accuracy:

```bash
lyricvid . --model medium.en
```

CUDA example:

```bash
lyricvid . --device cuda --compute-type float16
```

H.264 quality is controlled with CRF:

```bash
lyricvid . --crf 20
```

Lower CRF generally means higher quality and a larger MP4. The default is 24.

## README screenshot automation with Playwright

Instead of manually pausing a video and taking screenshots, generate reproducible documentation frames:

```bash
npm install --save-dev playwright
npx playwright install chromium
node scripts/capture-readme-frames.mjs ./lyric-videos/song.mp4
```

The script launches Chromium headlessly, loads the actual MP4, seeks to representative intro/middle/outro timestamps, and writes:

```text
docs/screenshots/intro.png
docs/screenshots/middle.png
docs/screenshots/outro.png
```

Commit the images and GitHub will show the intro and middle frame directly in this README.

## D2 documentation

Architecture is maintained as D2 source:

```text
docs/architecture.d2
```

Render it:

```bash
./scripts/render-docs.sh
```

Keeping the diagram source in Git means architecture changes can be reviewed alongside code changes.

## CI/CD

`.github/workflows/ci.yml` validates Python code, tests lyric extraction/alignment, builds the package, smoke-tests the CLI, and verifies the bundled Remotion runtime.

`.github/workflows/release.yml` handles tagged `v*` releases and distributable artifacts.

## Repository topics

Recommended GitHub topics:

```text
remotion
faster-whisper
ffmpeg
lyric-video
video-generation
youtube-api
python-cli
karaoke
speech-to-text
music-visualizer
content-automation
playwright
d2
```

## Security

Never commit OAuth client secrets or cached tokens. Keep `.secrets/` ignored. Treat generated YouTube tokens as account credentials.

## License

MIT — see [LICENSE](LICENSE).

## Release tagging

LyricVid includes a guarded release helper. After committing a version bump and confirming the working tree is clean, run:

```bash
./scripts/tag-release.sh
```

The script reads the version from `pyproject.toml`, creates an annotated `v<version>` tag, pushes the current branch and tag, and lets `.github/workflows/release.yml` build the distributions and create the GitHub Release. It refuses to tag a dirty working tree or overwrite an existing tag.
