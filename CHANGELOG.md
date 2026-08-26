# Changelog

## 0.9.2

- Add a repository-specific Secret Guard for YouTube/Google OAuth credentials, cached tokens, private keys, cloud/API keys, and embedded database passwords.
- Add Secret Guard self-tests and run the scanner in required CI validation.
- Document repo-specific credential remediation and add a security badge.
- Fix the Trivy action reference to the valid `v0.36.0` tag.

## 0.9.1

- Added Dependabot coverage for Python, npm, Docker, and GitHub Actions.
- Added CodeQL analysis for Python and JavaScript/TypeScript.
- Added Trivy filesystem vulnerability, secret, and misconfiguration scanning.
- Added pull-request dependency review and OpenSSF Scorecard workflow.
- Added weekly/manual end-to-end render smoke test with ffprobe media-contract validation.
- Added coverage collection, CODEOWNERS, issue/PR templates, CONTRIBUTING.md, and pre-commit hooks.
- Added branch-protection configuration helper and CycloneDX SBOM generation for releases.
- Bundled the illustrated wiki and vendored D2 icons with the release tree.

## 0.9.0

- Added layered CI repository validation, Python dependency auditing with `pip-audit`, static security analysis with `bandit`, D2 compilation checks, and a tracked-secret guard.
- Added Docker packaging plus GHCR publishing with branch/tag/SHA tags and build provenance attestations.
- Added `.dockerignore` protections so source media, OAuth material, tokens, virtualenvs, and render outputs never enter the container build context.
- Rebuilt README as a detailed operator guide covering installation, lyric policy, artwork, detached jobs, QA, secure OAuth handling, recommended private-to-public YouTube workflow, HD-processing checks, containers, docs tooling, CI/CD, and troubleshooting.
- Corrected project/repository metadata from the obsolete `lyricvid-cli-new` path to `iamrichmack111/lyricvid-cli`.
- Added idempotent GitHub completed-issue backfill tooling for the major capabilities developed through v0.9.0.
- Added a logical backfill commit helper that groups current changes without forging historical timestamps or authorship.
- Bumped package/runtime version consistency to 0.9.0.

## 0.8.2

- Fixed `docs/architecture.d2` by replacing the reserved D2 identifier `style` with `visual_preset`, so architecture rendering no longer fails on reserved-keyword edge errors.
- Installer now installs the LyricVid man page into the user manpath at `~/.local/share/man/man1/lyricvid.1`.
- Installer automatically renders `docs/architecture.svg` when D2 is already installed; missing D2 remains non-fatal.
- Release tagging continues to derive the annotated Git tag from the package version, so this release tags as `v0.8.2`.

## 0.8.1

- Fixed macOS pipx upgrades when pipx uses uv and a LyricVid venv already exists.
- Installer now resolves `PIPX_HOME`/`PIPX_BIN_DIR`, removes only stale LyricVid paths, and scopes `UV_VENV_CLEAR=1` to the reinstall.
- Added a release-tag helper that verifies the package version, clean working tree, and existing tags before creating/pushing an annotated Git tag.

## 0.8.0

- Rebuilt README with workflow badges, style matrix, YouTube notes, Playwright screenshot automation, and D2 documentation.
- Added a detailed Unix man page at `docs/lyricvid.1`.
- Added `scripts/capture-readme-frames.mjs` to capture intro/middle/outro frames from an actual rendered MP4 with Playwright.
- Added `docs/architecture.d2` plus `scripts/render-docs.sh` for architecture-as-code.
- Improved project metadata/description for GitHub and package discovery.
- Improved the pipx installer to recover cleanly from an existing/stale LyricVid environment.

## 0.2.0

- Prefer exact embedded media lyrics over Whisper-generated text.
- Support ID3 USLT/SYLT, MP4/M4A ©lyr, and common Vorbis/FLAC lyric tags.
- Preserve authored spelling, punctuation, capitalization, and line breaks.
- Use Whisper word timestamps as timing anchors and interpolate unmatched authored words.
- Add `--lyrics-info` and `--lyrics-source`.
- Add per-album `alignment-report.json` output.
- Expand CI across Python 3.10–3.12 with lyric/alignment tests and package validation.
- Add Remotion runtime CI smoke validation.
- Harden tagged GitHub Release CD with package/tag version checks.
- Remove `push-github.sh`; use standard Git commands.

## 0.1.0

- Initial installable LyricVid CLI.
- faster-whisper music transcription with VAD disabled.
- Remotion lyric-video rendering and transcript caching.

## 0.4.0
- YouTube descriptions can now come from `--description-file` (TXT/Markdown) or stdin.
- Automatic description sidecars: `<video>.description.txt`, `<video>.description.md`, or `<video>.youtube.txt`.
- Added `lyricvid upload --dry-run` to validate metadata before uploading.
- Added configurable resumable upload chunks with `--chunk-mb` (default 8 MiB).
- Added YouTube title/description length validation.

## 0.5.0
- Added ten coordinated `--style` presets for cyber, terminal, clean, podcast, explainer, and themed variants.
- Added `--detach` / `--background-job` for render and YouTube upload processes that survive terminal closure.
- Added `lyricvid jobs` to inspect recent detached processes and log locations.
- Added style-aware Remotion particle, grid, scanline, and background treatment.
- Preserved v0.4 description-file discovery, resumable YouTube uploads, ffprobe/embedded lyrics, Whisper alignment, PNG, background-video, voice-over, and output formats.

## 0.6.0
- Added true cover-art intro scenes with configurable `--intro-seconds`; music, voice-over, and lyric timing begin after the intro.
- Added cinematic cover fade-in/fade-out, slow zoom, glow, and crossfade into the main Remotion scene.
- Rebranded the top-left renderer label to configurable `--brand` (default: `Richmack Radio`).
- Added `--artist` with automatic fallback to embedded audio artist metadata.
- Moved song/artist metadata to the top-right safe area so it does not collide with centered lyrics.
- Preserves authored section markers such as `[Verse 1]`, `[Chorus]`, `[Bridge]`, and `[Outro]` as visual section labels instead of lyric words.
- Extended composition duration automatically when an intro is enabled.

## 0.7.0
- Added `metro-cinematic` visual preset for music-video/album-art treatments.
- Added configurable cover-art outros with `--outro-seconds`, `--outro-image`, and `--outro-text`.
- Added conservative lyric display windows and suppression of very short inferred timing spans to reduce lyric flashes between sung lines.
- Reduced preview/HUD clutter in the metro cinematic style.
