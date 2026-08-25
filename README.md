# LyricVid

LyricVid is an installable CLI that turns a folder of songs into animated Remotion lyric videos. **Exact lyrics embedded in the media metadata are used as the displayed source of truth; Whisper is used to determine when those exact words occur in the song.**

The CLI is installed separately from your music folders.

## What changed in v0.2.0

- Reads embedded exact lyrics before falling back to text sidecars.
- Supports MP3 ID3 `USLT` and `SYLT` lyric frames.
- Supports M4A/MP4 `©lyr` and common FLAC/Vorbis `LYRICS` / `UNSYNCEDLYRICS` tags.
- Preserves the exact authored spelling, punctuation, capitalization, and lyric line breaks in the video.
- Uses faster-whisper word timestamps only as timing anchors.
- Interpolates unmatched authored words between nearby Whisper anchors instead of replacing them with Whisper guesses.
- Writes `lyric-videos/alignment-report.json` for alignment QA.
- Adds `--lyrics-info` and `--lyrics-source` controls.
- CI tests Python 3.10–3.12, exact-lyric extraction/alignment, package builds, and the bundled Remotion runtime.
- Tagged releases build validated wheels/source distributions and attach them to GitHub Releases.
- `push-github.sh` has been removed. This is now a normal Git repository you can push with standard Git commands.

## Install after cloning/downloading

```bash
./install.sh
```

The installer uses `pipx`, so `lyricvid` is exposed on your PATH while its Python environment remains isolated.

## Install directly from GitHub

```bash
pipx install git+https://github.com/YOUR_USERNAME/lyricvid-cli.git
```

Upgrade later:

```bash
pipx upgrade lyricvid
```

## Use anywhere

From inside an album directory:

```bash
cd ~/Music/MyAlbum
lyricvid .
```

Or from anywhere:

```bash
lyricvid ~/Music/MyAlbum
```

Output is written to:

```text
~/Music/MyAlbum/lyric-videos/
```

## Exact lyric priority

Default `--lyrics-source auto` uses this order:

```text
1. Embedded media lyrics
2. Matching sidecar lyric file
3. Whisper transcription when no authored lyrics exist
```

Supported embedded metadata includes:

- MP3/ID3: `USLT`, `SYLT`
- M4A/MP4: `©lyr`
- FLAC/Ogg/Vorbis: `LYRICS`, `UNSYNCEDLYRICS`, and similar lyric fields

Matching sidecars are also supported:

```text
Terraform.mp3
Terraform.lyrics.txt
```

## Inspect lyric metadata before rendering

This does **not** load Whisper:

```bash
lyricvid ~/Music/MyAlbum --lyrics-info
```

Example output:

```text
✓ Terraform.mp3        embedded:USLT     410 words
✓ Set FACL.mp3         embedded:USLT     273 words
· Instrumental.mp3     Whisper only
```

Force a source when debugging:

```bash
lyricvid . --lyrics-source embedded
lyricvid . --lyrics-source sidecar
lyricvid . --lyrics-source whisper
```

## How alignment works

```text
Embedded exact lyrics
        ↓
Exact authored words + line breaks
        ↓
Whisper listens to the full song
(VAD OFF for music)
        ↓
Whisper word timing anchors
        ↓
Sequence alignment
        ↓
Unmatched exact words interpolated
between neighboring timing anchors
        ↓
Remotion karaoke rendering
```

Whisper can hear `T Shark` while the metadata says `TShark`; the video still displays **TShark**. Whisper contributes the timing, not the final spelling.

## Useful commands

Render:

```bash
lyricvid .
```

Inspect embedded lyrics only:

```bash
lyricvid . --lyrics-info
```

Transcribe/align without rendering:

```bash
lyricvid . --transcribe-only
```

Preview in Remotion Studio:

```bash
lyricvid . --studio
```

Overwrite existing videos without forcing new Whisper transcription:

```bash
lyricvid . --force
```

Force new Whisper timing data:

```bash
lyricvid . --retranscribe
```

Stronger model:

```bash
lyricvid . --model medium.en
```

CUDA:

```bash
lyricvid . --device cuda --compute-type float16
```

Recursive discovery:

```bash
lyricvid ~/Music --recursive
```

Custom output:

```bash
lyricvid . -o ~/Videos/MyAlbum
```

Dependency check:

```bash
lyricvid --doctor
```

Clear cached Whisper/Remotion data:

```bash
lyricvid --clean-cache
```

## Alignment report

Each render creates:

```text
lyric-videos/alignment-report.json
```

It records the lyric source, direct Whisper anchor coverage, authored word count, and line count for every track. This makes low-confidence tracks easy to spot without watching every video end to end.

## CI/CD

### CI

`.github/workflows/ci.yml` runs on pushes, pull requests, and manual dispatch. It:

- tests Python 3.10, 3.11, and 3.12
- compiles the source
- runs unit tests for embedded ID3 lyrics and exact-text alignment
- builds wheel + source distribution
- validates package metadata with `twine check`
- installs the built wheel and smoke-tests the CLI
- verifies Remotion package versions stay aligned
- installs and bundles the Remotion runtime as a smoke test
- uploads built distributions as GitHub Actions artifacts

### CD

`.github/workflows/release.yml` runs on `v*` tags. It:

- verifies the Git tag matches `pyproject.toml`
- builds wheel + source distribution
- validates both distributions
- uploads build artifacts
- creates a GitHub Release containing the installable packages

Release v0.2.0:

```bash
git tag v0.2.0
git push origin v0.2.0
```

## Push to your own GitHub repo

There is no custom push script. Use standard Git:

```bash
git remote add origin git@github.com:YOUR_USERNAME/lyricvid-cli.git
git push -u origin main
```

## Requirements

- Python 3.10+
- Node.js + npm
- Linux or macOS recommended

The first actual render installs the bundled Remotion Node runtime under `~/.cache/lyricvid`. Whisper transcripts are cached under the same LyricVid cache tree.

## License

MIT
