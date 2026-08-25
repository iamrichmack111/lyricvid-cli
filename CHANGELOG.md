# Changelog

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
