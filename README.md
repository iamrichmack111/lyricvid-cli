# LyricVid

[![CI](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/ci.yml)
[![Container](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/container.yml/badge.svg)](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/container.yml)
[![Release](https://img.shields.io/github/v/release/iamrichmack111/lyricvid-cli?display_name=tag)](https://github.com/iamrichmack111/lyricvid-cli/releases)
[![GHCR](https://img.shields.io/badge/package-ghcr.io%2Fiamrichmack111%2Flyricvid--cli-2496ED?logo=docker&logoColor=white)](https://github.com/iamrichmack111/lyricvid-cli/pkgs/container/lyricvid-cli)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Remotion](https://img.shields.io/badge/Remotion-4.x-6C63FF)](https://www.remotion.dev/)
[![faster-whisper](https://img.shields.io/badge/Whisper-faster--whisper-orange)](https://github.com/SYSTRAN/faster-whisper)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-007808)](https://ffmpeg.org/)
[![YouTube API](https://img.shields.io/badge/YouTube-Data%20API%20v3-FF0000)](https://developers.google.com/youtube/v3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CodeQL](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/codeql.yml/badge.svg)](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/codeql.yml)
[![Supply Chain](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/supply-chain.yml/badge.svg)](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/supply-chain.yml)
[![Integration Render](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/integration.yml/badge.svg)](https://github.com/iamrichmack111/lyricvid-cli/actions/workflows/integration.yml)

**LyricVid is a terminal-driven video production pipeline for Whisper-aligned lyric videos, album-art visualizers, narrated explainers, social formats, detached rendering, and secure YouTube publishing.**

LyricVid tries to keep authored lyrics as the display source of truth. It probes embedded/container metadata with ffprobe and Mutagen, can use sidecar lyric files, and uses **faster-whisper primarily as an acoustic timing layer**. The aligned result is rendered with Remotion, encoded with FFmpeg, and can be uploaded to YouTube through OAuth 2.0.

## What it can do

- Preserve authored spelling, punctuation, capitalization, and section labels while using Whisper timing.
- Render animated lyrics with Remotion and H.264 output through FFmpeg.
- Use PNG/JPG/WebP album art as a background, card, logo, intro, or outro.
- Add looping background video and optional narration/voice-over.
- Produce landscape, vertical Shorts/Reels/TikTok, and square variants.
- Use coordinated visual presets including `cyberpunk`, `neon-pink`, and `metro-cinematic`.
- Run long renders and uploads as detached jobs that survive terminal closure.
- Upload to YouTube with title, description files, tags, category, privacy, resumable chunks, and dry-run validation.
- Capture README screenshots from the actual rendered MP4 with Playwright.
- Maintain architecture documentation as D2 source.
- Ship as a Python CLI and a GHCR container image.

## Architecture

The reviewable source is [`docs/architecture.d2`](docs/architecture.d2).

```bash
./scripts/render-docs.sh
open docs/architecture.svg    # macOS
```

```text
Audio / lyrics / art / narration
              │
      ┌───────┴────────┐
      ▼                ▼
ffprobe + Mutagen   faster-whisper
      │                │
      └───────┬────────┘
              ▼
     exact-text alignment
              │
              ▼
           Remotion
     intro → lyrics → outro
              │
              ▼
            FFmpeg
              │
        ┌─────┴─────┐
        ▼           ▼
 detached jobs   YouTube API
```

## Preview documentation

The repo can generate deterministic screenshots from a finished MP4 instead of manually pausing a player:

```bash
npm install --save-dev playwright
npx playwright install chromium
node scripts/capture-readme-frames.mjs ./lyric-videos/song.mp4
```

That writes:

```text
docs/screenshots/intro.png
docs/screenshots/middle.png
docs/screenshots/outro.png
```

When those files are committed, the README can show the actual intro and lyric scene:

| Intro | Mid-song lyric scene |
| --- | --- |
| ![LyricVid intro](docs/screenshots/intro.png) | ![LyricVid middle](docs/screenshots/middle.png) |

## Requirements

Recommended local stack:

- Python 3.10+
- `pipx`
- Node.js + npm
- FFmpeg / ffprobe
- D2 only if you want to rebuild the architecture SVG
- Google OAuth Desktop credentials only if you want YouTube uploads

On macOS with Homebrew:

```bash
brew install ffmpeg pipx d2
pipx ensurepath
```

Node can be installed with Homebrew or a version manager such as nvm.

## Installation

Clone the actual repository and install:

```bash
git clone git@github.com:iamrichmack111/lyricvid-cli.git
cd lyricvid-cli
./install.sh
```

The installer is designed to recover from stale LyricVid pipx/uv environments rather than deleting unrelated environments.

Verify:

```bash
lyricvid --version
lyricvid --doctor
lyricvid styles
```

The man page is installed into the user man path when possible:

```bash
man lyricvid
```

You can also open the repository copy directly:

```bash
man ./docs/lyricvid.1
```

## Quick start

Put one or more audio files in a working folder and render the folder:

```bash
cd ~/Music/my-project
lyricvid .
```

Output defaults to:

```text
./lyric-videos/
```

A branded album-art render:

```bash
lyricvid . \
  --style metro-cinematic \
  --image cover.png \
  --artist "Esoterica" \
  --brand "Richmack Radio" \
  --intro-seconds 5 \
  --outro-seconds 7 \
  --outro-text "COMPETE FOR YOU — ESOTERICA" \
  --detach
```

Check detached jobs later:

```bash
lyricvid jobs
```

## Recommended project layout

Keeping each release in its own directory makes metadata, artwork, and upload state easy to reason about:

```text
compete-for-you/
├── Compete for You.mp3
├── cover.png
├── description.md
├── Compete for You.lyrics.txt        # optional authored lyric sidecar
├── .secrets/                         # local only, never commit
│   ├── youtube-oauth.json
│   └── youtube-token.json
└── lyric-videos/
    ├── compete-for-you.mp4
    └── alignment-report.json
```

`.secrets/`, OAuth JSON files, cached tokens, rendered videos, and source audio are ignored by Git in this repository.

## Lyric source policy

With `--lyrics-source auto`, LyricVid prefers authored text when available:

```text
container / embedded lyric metadata
             ↓
      Mutagen lyric tags
             ↓
       sidecar lyrics
             ↓
 Whisper-only text when no authored text exists
```

Whisper is still used to listen to the performance and provide timing anchors. This allows authored text to remain correct even when speech recognition would spell a technical term, artist phrase, or stylized lyric differently.

Inspect what LyricVid found without rendering:

```bash
lyricvid . --lyrics-info
```

Transcribe/align without producing the MP4:

```bash
lyricvid . --transcribe-only
```

Force new Whisper timing rather than using the transcript cache:

```bash
lyricvid . --retranscribe --force
```

An `alignment-report.json` can be used to inspect alignment quality before publishing.

### Section markers

Authored markers such as these are treated as structure rather than sung words:

```text
[Verse 1]
[Chorus]
[Bridge]
[Outro]
```

Lyric display windows are conservative and non-overlapping to reduce brief text flashes between performed lines.

## Visual styles

List installed styles:

```bash
lyricvid styles
```

| Style | Suggested use |
| --- | --- |
| `cyberpunk` | High-energy neon lyric videos |
| `terminal-green` | CLI, hacker, command-line material |
| `daemon-red` | Aggressive ops/infrastructure visuals |
| `root-violet` | Dark violet cinematic material |
| `system-amber` | Retro-computing treatment |
| `network-teal` | Cloud/networking songs and explainers |
| `neon-pink` | Pop/R&B and social-first videos |
| `minimal-clean` | Reduced effects and clean artwork |
| `podcast` | Commentary, narration, audio shows |
| `explainer` | Technical diagrams and voice-over |
| `metro-cinematic` | Album-art music video with restrained neon/metro mood |

## Artwork, intro, and outro

Use cover art:

```bash
lyricvid . --image cover.png --image-mode card
```

Artwork modes:

```text
background
card
logo
```

Add a cover-art intro and outro:

```bash
lyricvid . \
  --image cover.png \
  --intro-seconds 5 \
  --outro-seconds 7 \
  --outro-text "THANKS FOR LISTENING"
```

If `--outro-image` is not supplied, the primary image can be reused.

## Voice-over and motion backgrounds

Narration over music:

```bash
lyricvid . \
  --style explainer \
  --voiceover narration.mp3 \
  --music-volume 0.25 \
  --voiceover-volume 1.0
```

Loop a background video:

```bash
lyricvid . \
  --background-video terminal-loop.mp4 \
  --style cyberpunk
```

## Output formats and quality

Landscape YouTube:

```bash
lyricvid . --format landscape
```

Vertical Shorts / Reels / TikTok:

```bash
lyricvid . --format short
```

Square:

```bash
lyricvid . --format square
```

H.264 quality is controlled with CRF:

```bash
lyricvid . --crf 20
```

Lower CRF generally means better quality and a larger file. Do not judge final YouTube quality immediately after upload: YouTube often exposes its low-resolution transcode before HD processing finishes.

## Detached rendering

Start a render that survives terminal closure or an SSH disconnect:

```bash
lyricvid . --style metro-cinematic --detach
```

LyricVid prints the job ID, PID, log path, and a `tail -f` command. You can leave the shell and inspect jobs later:

```bash
lyricvid jobs
```

Logs/metadata live under:

```text
~/.cache/lyricvid/jobs/
```

## YouTube setup

1. Create or select a Google Cloud project.
2. Enable **YouTube Data API v3**.
3. Configure the Google OAuth consent screen.
4. Create an OAuth client of type **Desktop app**.
5. Download the client JSON locally.
6. Never commit that JSON or the generated OAuth token.

For the current project-local flow:

```bash
mkdir -p .secrets
cp ~/Downloads/client_secret_*.json .secrets/youtube-oauth.json
chmod 600 .secrets/youtube-oauth.json
```

The first upload can open the browser for authorization and write a cached token under `.secrets/`.

### Credential safety

Never place real values in README examples. Never commit:

```text
.secrets/
client_secret_*.json
youtube-oauth.json
youtube-token.json
credentials.json
```

Run the same repository credential check used by CI:

```bash
./scripts/validate-no-secrets.sh
```

If a real credential is ever committed, deleting the file in a later commit is not sufficient: rotate/revoke it and remove it from Git history before publishing.

## Recommended YouTube workflow

### 1. Prepare the project

```bash
mkdir -p ~/Downloads/compete-for-you
cp ~/Downloads/'Compete for You.mp3' ~/Downloads/compete-for-you/
cd ~/Downloads/compete-for-you
```

Add `cover.png`, an optional authored lyric sidecar, and `description.md`.

### 2. Inspect lyrics before a long render

```bash
lyricvid . --lyrics-info
lyricvid . --transcribe-only
```

Review `alignment-report.json` if timing is important.

### 3. Render privately from the terminal

```bash
lyricvid . \
  --style metro-cinematic \
  --image cover.png \
  --artist "Esoterica" \
  --brand "Richmack Radio" \
  --intro-seconds 5 \
  --outro-seconds 7 \
  --force \
  --detach
```

Use `lyricvid jobs` until it finishes, then play the generated MP4 locally. Check the intro, first verse, chorus/section transitions, midpoint, and outro before upload.

### 4. Validate YouTube metadata without uploading

```bash
VIDEO="$(find ./lyric-videos -type f -name '*.mp4' -print0 | xargs -0 ls -t | head -1)"

lyricvid upload "$VIDEO" \
  --title "Esoterica - Compete for You | Official Lyric Video" \
  --description-file description.md \
  --tags "Esoterica,Compete for You,R&B,lyric video,Richmack Radio" \
  --dry-run
```

### 5. First upload: private

Use a private upload first when validating OAuth or a new production workflow:

```bash
lyricvid upload "$VIDEO" \
  --title "Esoterica - Compete for You | Official Lyric Video" \
  --description-file description.md \
  --tags "Esoterica,Compete for You,R&B,lyric video,Richmack Radio"
```

No `--public` or `--unlisted` means private.

### 6. Public upload

Once the local render and metadata are verified:

```bash
lyricvid upload "$VIDEO" \
  --title "Esoterica - Compete for You | Official Lyric Video" \
  --description-file description.md \
  --tags "Esoterica,Compete for You,R&B,lyric video,Richmack Radio" \
  --public
```

After OAuth has already been established, an upload can also be detached:

```bash
lyricvid upload "$VIDEO" \
  --title "Esoterica - Compete for You | Official Lyric Video" \
  --description-file description.md \
  --public \
  --detach
```

### Why YouTube may initially show 360p

YouTube frequently makes an SD transcode available before higher-resolution processing finishes. The presence of 360p shortly after upload does not prove the source render was 360p. Verify the local MP4 resolution with ffprobe and allow YouTube time to finish HD processing:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height \
  -of csv=s=x:p=0 "$VIDEO"
```

## Container image

The repository publishes a package to:

```text
ghcr.io/iamrichmack111/lyricvid-cli
```

Pull it:

```bash
docker pull ghcr.io/iamrichmack111/lyricvid-cli:latest
```

Check the CLI:

```bash
docker run --rm ghcr.io/iamrichmack111/lyricvid-cli:latest --version
```

Render a host project by mounting it into `/work`:

```bash
docker run --rm \
  -v "$PWD:/work" \
  ghcr.io/iamrichmack111/lyricvid-cli:latest \
  . --style cyberpunk
```

Do **not** bake OAuth credentials into an image. If containerized YouTube upload is needed, mount the local `.secrets` directory at runtime rather than copying it into the Dockerfile or build context.

## Remotion Studio

Prepare the project and open Studio:

```bash
lyricvid . --studio
```

Use Studio for interactive visual iteration, but use the CLI for reproducible final renders.

## Documentation tooling

Render D2 architecture:

```bash
./scripts/render-docs.sh
```

Capture real video frames with Playwright:

```bash
node scripts/capture-readme-frames.mjs ./lyric-videos/song.mp4
```

Open the man page:

```bash
man lyricvid
```

## CI/CD and validation

The CI pipeline is intentionally layered:

1. **Repository validation** — shell syntax, version consistency, D2 compilation, and secret-path/content checks.
2. **Security** — `pip-audit` dependency audit and `bandit` static analysis.
3. **Compatibility** — tests across supported Python versions plus wheel/sdist build and `twine check`.
4. **Container validation** — build the Docker image without publishing on normal CI.
5. **Container CD** — publish version/SHA/latest tags to GHCR and attach provenance attestations.
6. **Release CD** — tagged releases verify the package/tag version before creating GitHub Release assets.

No Google OAuth credential is required in CI or CD. YouTube publishing is deliberately a local authenticated operation rather than a repository secret-dependent pipeline.

Run core validation locally:

```bash
./scripts/validate-no-secrets.sh
python -m compileall -q src
pytest -q
python -m build
twine check dist/*
./scripts/render-docs.sh
```

## Backfilling completed engineering work

The repository includes an idempotent helper to create GitHub issues for major completed capabilities and immediately close them as completed:

```bash
./scripts/backfill-issues.sh
```

It checks titles before creating issues so repeated runs do not intentionally duplicate the same backfill items.

For a repository clone where the v0.9.1 files have been overlaid but not committed, create a **truthful present-day logical commit series** with:

```bash
./scripts/backfill-commits.sh
```

The script groups changes by security, container packaging, documentation, maintenance, and release preparation. It **does not forge old commit timestamps or authorship**.

## GitHub metadata

Update the description and topics using the authenticated GitHub CLI:

```bash
./scripts/update-github-metadata.sh
```

Recommended topics include Remotion, faster-whisper, FFmpeg, lyric-video, video-generation, YouTube API, Python CLI, music visualizer, content automation, Playwright, D2, GHCR, and OAuth.


## Repository security and supply-chain controls

LyricVid treats generated media and YouTube OAuth material as local runtime data, not repository assets. CI/CD is intentionally capable of building, testing, scanning, packaging, and releasing the project without any Google credential.

The repository now uses several complementary controls:

- **Dependabot** monitors Python, the bundled Remotion npm runtime, Docker, and GitHub Actions dependencies.
- **CodeQL** analyzes Python and JavaScript/TypeScript on pushes, pull requests, and a weekly schedule.
- **Trivy** scans the repository for high/critical vulnerabilities, secrets, and configuration problems.
- **Dependency Review** rejects pull requests that introduce high-severity vulnerable dependencies and selected incompatible licenses.
- **OpenSSF Scorecard** evaluates supply-chain posture and uploads results to code scanning.
- Existing **Bandit**, **pip-audit**, **npm audit**, and LyricVid's custom credential validator remain part of CI.
- A weekly/manual **real render smoke test** generates a short MP4 and verifies H.264, resolution, and audio with ffprobe.
- Tagged releases generate a **CycloneDX SBOM** in addition to package/container provenance.
- `.pre-commit-config.yaml`, `CODEOWNERS`, structured issue templates, and a PR checklist make local and review-time validation repeatable.

Install local contribution hooks with:

```bash
python -m pip install '.[dev]'
pre-commit install
pre-commit run --all-files
```

Repository administrators can apply the supplied main-branch protection baseline after the named checks have run at least once:

```bash
./scripts/configure-branch-protection.sh iamrichmack111/lyricvid-cli main
```

The helper disables force-push/deletion, requests linear history and resolved conversations, and requires the core validation/security checks. Review the resulting rules in GitHub Settings because available branch/ruleset features depend on repository visibility and plan.

## Release workflow

After all changes are committed and CI is green:

```bash
./scripts/tag-release.sh
```

The helper reads the version from `pyproject.toml`, refuses a dirty tree or duplicate tag, creates an annotated `v<version>` tag, and pushes it. The tag triggers the GitHub release workflow and container image version tag.

## Troubleshooting

### `pipx` says the LyricVid venv already exists

Use the current `./install.sh`; it contains recovery logic for stale LyricVid pipx/uv environments. Avoid manually deleting unrelated pipx environments.

### `OAuth credentials not found`

Confirm the current project contains:

```text
.secrets/youtube-oauth.json
```

and verify the file is not tracked:

```bash
git status --ignored .secrets/
./scripts/validate-no-secrets.sh
```

### Whisper appears stuck after an HF Hub warning

A first model download or CPU transcription can be quiet for a while. Check whether the detached process is alive and consuming CPU, and inspect `lyricvid jobs` rather than assuming it has hung.

### D2 rejects a diagram with “reserved keywords”

Use the current `docs/architecture.d2`; the previous reserved `style` identifier was replaced with `visual_preset`.

## License

MIT — see [LICENSE](LICENSE).
