# Contributing to LyricVid

LyricVid combines Python, faster-whisper, FFmpeg, Remotion/TypeScript, D2 documentation, container packaging, and YouTube OAuth. Changes should preserve both media correctness and credential safety.

## Development setup

```bash
git clone git@github.com:iamrichmack111/lyricvid-cli.git
cd lyricvid-cli
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q
```

Install Node/npm, FFmpeg/ffprobe, and optionally D2 for runtime/docs work.

## Before a pull request

```bash
pytest -q
./scripts/validate-no-secrets.sh
./scripts/render-docs.sh
./scripts/render-wiki.sh
python -m build
```

For shell changes, run `bash -n` on the modified script. For Remotion changes, validate the TypeScript/runtime package and, when practical, run the integration render workflow.

## Security rules

Never commit `.secrets/`, Google OAuth client JSON, generated token JSON, API keys, raw private media, or secrets copied into examples. If a real secret is committed, revoke/rotate it and remove it from history; deleting it in a later commit is not enough.

## Commit style

Prefer scoped, imperative commits such as:

- `feat: add metro cinematic preset`
- `fix: suppress inferred lyric flashes`
- `security: add dependency review gate`
- `docs: expand YouTube production workflow`

## Releases

Release tags must match the version in `pyproject.toml`. Run the normal validation suite before `scripts/tag-release.sh`.
