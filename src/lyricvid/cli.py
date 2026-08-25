from __future__ import annotations

import argparse
import hashlib
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__

CACHE_ROOT = Path.home() / ".cache" / "lyricvid"
RUNTIME_ROOT = CACHE_ROOT / "remotion-runtime"
TRANSCRIPT_CACHE = CACHE_ROOT / "transcripts"
RUNTIME_VERSION = "0.2.0-remotion-4.0.516"

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg", ".opus"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv"}

THEMES = [
    {"accent": "#52F7FF", "accent2": "#7C5CFF", "name": "CYBER BLUE"},
    {"accent": "#72FF79", "accent2": "#00D9FF", "name": "TERMINAL GREEN"},
    {"accent": "#FF4B55", "accent2": "#FF8A00", "name": "DAEMON RED"},
    {"accent": "#FF55E8", "accent2": "#6B5CFF", "name": "ROOT VIOLET"},
    {"accent": "#FFD84D", "accent2": "#FF5C35", "name": "SYSTEM AMBER"},
    {"accent": "#00FFA8", "accent2": "#1B78FF", "name": "NETWORK TEAL"},
    {"accent": "#FF77AA", "accent2": "#26DDFF", "name": "NEON PINK"},
]


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "track"


def title_for(path: Path) -> str:
    # Clean common duplicate suffixes such as "Song(3).mp3".
    return re.sub(r"\s*\(\d+\)$", "", path.stem).strip()


def require_program(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise SystemExit(
            f"ERROR: '{name}' is required. Install it, then run lyricvid again."
        )
    return found


def run(command: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def copy_tree_contents(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def ensure_runtime() -> Path:
    """Create one shared Remotion runtime outside the music folders."""
    require_program("node")
    require_program("npm")

    marker = RUNTIME_ROOT / ".runtime-version"
    remotion_bin = RUNTIME_ROOT / "node_modules" / ".bin" / "remotion"

    if (
        marker.exists()
        and marker.read_text(encoding="utf-8").strip() == RUNTIME_VERSION
        and remotion_bin.exists()
    ):
        return RUNTIME_ROOT

    print("\nSetting up LyricVid's Remotion runtime (first run only)...")

    if RUNTIME_ROOT.exists():
        shutil.rmtree(RUNTIME_ROOT)

    template = Path(__file__).resolve().parent / "remotion_runtime"
    copy_tree_contents(template, RUNTIME_ROOT)

    run(
        ["npm", "install", "--no-audit", "--no-fund"],
        cwd=RUNTIME_ROOT,
    )

    marker.write_text(RUNTIME_VERSION + "\n", encoding="utf-8")
    print("✓ Remotion runtime ready")
    return RUNTIME_ROOT


def audio_duration(path: Path) -> float:
    from mutagen import File as MutagenFile

    media = MutagenFile(path)
    if media is None or getattr(media, "info", None) is None:
        raise RuntimeError(f"Could not read audio duration: {path}")
    return float(media.info.length)


def find_files(folder: Path, extensions: set[str], recursive: bool) -> list[Path]:
    iterator = folder.rglob("*") if recursive else folder.iterdir()
    return sorted(
        [p for p in iterator if p.is_file() and p.suffix.lower() in extensions],
        key=lambda p: str(p).lower(),
    )


def order_audio(folder: Path, songs: list[Path]) -> list[Path]:
    """Honor playlist.m3u if one is present, then append undiscovered tracks."""
    playlist = folder / "playlist.m3u"
    if not playlist.exists():
        return songs

    ordered: list[Path] = []
    song_set = {p.resolve(): p for p in songs}

    for raw in playlist.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        candidate = (folder / line).resolve()
        if candidate in song_set and song_set[candidate] not in ordered:
            ordered.append(song_set[candidate])

    for song in songs:
        if song not in ordered:
            ordered.append(song)
    return ordered


def _clean_lyrics_text(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    if isinstance(value, (list, tuple)):
        parts = [_clean_lyrics_text(item) for item in value]
        value = "\n".join(part for part in parts if part)
    elif not isinstance(value, str):
        value = str(value)

    value = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    return value or None


def lyrics_from_tags(tags) -> tuple[str | None, str | None]:
    """Extract exact lyrics from common Mutagen tag containers."""
    if tags is None:
        return None, None

    # ID3 synchronized lyrics. We use the authored text as source-of-truth and
    # still let Whisper provide the timing because SYLT timing quality varies.
    if hasattr(tags, "getall"):
        try:
            sylt_frames = tags.getall("SYLT")
        except Exception:
            sylt_frames = []
        for frame in sylt_frames:
            entries = getattr(frame, "text", None) or []
            text = " ".join(str(item[0]) for item in entries if item and str(item[0]).strip())
            cleaned = _clean_lyrics_text(text)
            if cleaned:
                return cleaned, "embedded:SYLT"

        try:
            uslt_frames = tags.getall("USLT")
        except Exception:
            uslt_frames = []
        candidates = []
        for frame in uslt_frames:
            cleaned = _clean_lyrics_text(getattr(frame, "text", None))
            if cleaned:
                candidates.append(cleaned)
        if candidates:
            # Prefer the longest complete lyric payload when multiple languages
            # or descriptions are embedded.
            return max(candidates, key=len), "embedded:USLT"

    # MP4/M4A and Vorbis/FLAC style mappings.
    preferred_keys = (
        "\xa9lyr",
        "lyrics",
        "LYRICS",
        "unsyncedlyrics",
        "UNSYNCEDLYRICS",
        "unsynced_lyrics",
        "UNSYNCED_LYRICS",
    )
    for key in preferred_keys:
        try:
            value = tags.get(key)
        except Exception:
            value = None
        cleaned = _clean_lyrics_text(value)
        if cleaned:
            return cleaned, f"embedded:{key}"

    # Last-resort generic lookup for tag names containing "lyric".
    try:
        keys = list(tags.keys())
    except Exception:
        keys = []
    for key in keys:
        if "lyric" not in str(key).lower():
            continue
        try:
            value = tags[key]
        except Exception:
            continue
        cleaned = _clean_lyrics_text(value)
        if cleaned:
            return cleaned, f"embedded:{key}"

    return None, None


def embedded_lyrics(song: Path) -> tuple[str | None, str | None]:
    from mutagen import File as MutagenFile

    try:
        media = MutagenFile(song, easy=False)
    except Exception:
        media = None

    if media is not None:
        text, source = lyrics_from_tags(getattr(media, "tags", None))
        if text:
            return text, source

    # ID3 can still be readable even when Mutagen cannot identify the audio
    # stream (for example partially written MP3 files).
    if song.suffix.lower() == ".mp3":
        try:
            from mutagen.id3 import ID3

            return lyrics_from_tags(ID3(song))
        except Exception:
            pass

    return None, None


def sidecar_lyrics(song: Path) -> tuple[str | None, str | None]:
    candidates = [
        song.with_suffix(".lyrics.txt"),
        song.with_suffix(".txt"),
        song.parent / f"{song.stem}.lyrics",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            text = _clean_lyrics_text(
                candidate.read_text(encoding="utf-8", errors="ignore")
            )
            if text:
                return text, f"sidecar:{candidate.name}"
    return None, None


def exact_lyrics(song: Path, source_policy: str = "auto") -> tuple[str | None, str | None]:
    """Resolve authored lyrics. Auto prefers embedded metadata over sidecars."""
    if source_policy == "whisper":
        return None, None
    if source_policy in ("auto", "embedded"):
        text, source = embedded_lyrics(song)
        if text:
            return text, source
        if source_policy == "embedded":
            return None, None
    if source_policy in ("auto", "sidecar"):
        return sidecar_lyrics(song)
    return None, None


def transcript_key(
    song: Path,
    model: str,
    language: str,
    lyrics_text: str | None,
    lyrics_source: str | None,
) -> str:
    stat = song.stat()
    lyrics_fingerprint = "none"
    if lyrics_text:
        lyrics_fingerprint = hashlib.sha256(lyrics_text.encode("utf-8")).hexdigest()

    raw = "|".join(
        [
            str(song.resolve()),
            str(stat.st_size),
            str(stat.st_mtime_ns),
            model,
            language,
            lyrics_source or "none",
            lyrics_fingerprint,
            "exact-lyrics-alignment-v1-word-timestamps-vad-off",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _normalize_alignment_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _authored_lyric_tokens(lyrics_text: str) -> tuple[list[dict], list[str]]:
    tokens: list[dict] = []
    lines: list[str] = []

    for raw_line in lyrics_text.splitlines():
        line = raw_line.strip()
        # Strip common LRC timestamps while preserving the authored lyric text.
        line = re.sub(r"^(?:\[\d{1,2}:\d{2}(?:\.\d+)?\])+", "", line).strip()
        if not line:
            continue
        # Section headers are useful metadata, but should not be sung/displayed
        # as lyric words unless they contain ordinary lyric text too.
        if re.fullmatch(r"\[[^\]]+\]", line) or re.fullmatch(r"\([^\)]+\)", line):
            continue

        line_index = len(lines)
        line_tokens = []
        for raw_token in re.findall(r"\S+", line):
            norm = _normalize_alignment_token(raw_token)
            if not norm:
                continue
            line_tokens.append(
                {
                    "text": raw_token,
                    "norm": norm,
                    "line": line_index,
                }
            )

        if line_tokens:
            lines.append(line)
            tokens.extend(line_tokens)

    return tokens, lines


def align_exact_lyrics(
    lyrics_text: str,
    whisper_words: list[dict],
    song_duration: float,
) -> tuple[list[dict], float, int]:
    """Use authored lyric text, with Whisper words only as timing anchors."""
    authored, original_lines = _authored_lyric_tokens(lyrics_text)
    if not authored:
        return group_words(whisper_words), 0.0, 0
    if not whisper_words:
        # Last-resort uniform timing across the song.
        span = max(song_duration, len(authored) * 0.08)
        step = span / max(1, len(authored))
        timed = []
        for i, token in enumerate(authored):
            start = i * step
            timed.append({**token, "start": start, "end": max(start + 0.04, (i + 1) * step)})
    else:
        lyric_norm = [item["norm"] for item in authored]
        whisper_norm = [_normalize_alignment_token(item["text"]) for item in whisper_words]

        matcher = difflib.SequenceMatcher(None, lyric_norm, whisper_norm, autojunk=False)
        mapping: dict[int, int] = {}
        for block in matcher.get_matching_blocks():
            for offset in range(block.size):
                mapping[block.a + offset] = block.b + offset

        timed: list[dict | None] = [None] * len(authored)
        for lyric_i, whisper_i in mapping.items():
            word = whisper_words[whisper_i]
            start = float(word["start"])
            timed[lyric_i] = {
                **authored[lyric_i],
                "start": start,
                "end": max(float(word["end"]), start + 0.04),
            }

        anchors = sorted(mapping)
        boundaries = [-1] + anchors + [len(authored)]
        first_speech = float(whisper_words[0]["start"])
        last_speech = float(whisper_words[-1]["end"])

        for b in range(len(boundaries) - 1):
            left = boundaries[b]
            right = boundaries[b + 1]
            missing = list(range(left + 1, right))
            if not missing:
                continue

            if left >= 0 and timed[left] is not None:
                window_start = float(timed[left]["end"])
            else:
                window_start = max(0.0, first_speech - 0.24 * len(missing))

            if right < len(authored) and timed[right] is not None:
                window_end = float(timed[right]["start"])
            else:
                window_end = max(window_start, min(song_duration, last_speech + 0.24 * len(missing)))

            if window_end <= window_start:
                window_end = window_start + 0.08 * len(missing)

            step = (window_end - window_start) / max(1, len(missing))
            for offset, lyric_i in enumerate(missing):
                start = window_start + offset * step
                end = window_start + (offset + 1) * step
                timed[lyric_i] = {
                    **authored[lyric_i],
                    "start": max(0.0, start),
                    "end": max(start + 0.04, end),
                }

        # mypy-friendly narrowing; every slot is filled above.
        timed = [item for item in timed if item is not None]

    grouped: list[dict] = []
    for line_index, exact_line in enumerate(original_lines):
        words = [item for item in timed if item["line"] == line_index]
        if not words:
            continue
        grouped.append(
            {
                "start": words[0]["start"],
                "end": max(words[-1]["end"], words[0]["start"] + 0.04),
                "text": exact_line,
                "words": [
                    {
                        "text": word["text"],
                        "start": word["start"],
                        "end": word["end"],
                    }
                    for word in words
                ],
            }
        )

    matched = 0
    if whisper_words:
        lyric_norm = [item["norm"] for item in authored]
        whisper_norm = [_normalize_alignment_token(item["text"]) for item in whisper_words]
        matcher = difflib.SequenceMatcher(None, lyric_norm, whisper_norm, autojunk=False)
        matched = sum(block.size for block in matcher.get_matching_blocks())
    coverage = matched / max(1, len(authored))
    return grouped, coverage, len(authored)

def group_words(words: list[dict]) -> list[dict]:
    lines: list[dict] = []
    current: list[dict] = []

    def flush() -> None:
        nonlocal current
        if not current:
            return
        text = " ".join(word["text"] for word in current)
        text = re.sub(r"\s+([,.!?;:])", r"\1", text).strip()
        lines.append(
            {
                "start": current[0]["start"],
                "end": max(current[-1]["end"], current[0]["start"] + 0.04),
                "text": text,
                "words": current.copy(),
            }
        )
        current = []

    for index, word in enumerate(words):
        current.append(word)
        following = words[index + 1] if index + 1 < len(words) else None
        pause = following["start"] - word["end"] if following else 0.0
        line_duration = current[-1]["end"] - current[0]["start"]
        punctuation = bool(re.search(r"[.!?]$", word["text"]))
        comma = bool(re.search(r"[,;:]$", word["text"]))

        if (
            len(current) >= 7
            or line_duration >= 4.2
            or pause >= 0.55
            or (punctuation and len(current) >= 3)
            or (comma and len(current) >= 5)
        ):
            flush()

    flush()
    return lines


def transcribe_song(
    model,
    song: Path,
    model_name: str,
    language: str,
    retranscribe: bool,
    lyrics_source_policy: str,
    song_duration: float,
) -> tuple[list[dict], int, str | None, float, int]:
    TRANSCRIPT_CACHE.mkdir(parents=True, exist_ok=True)
    lyrics_text, lyrics_source = exact_lyrics(song, lyrics_source_policy)
    cache = TRANSCRIPT_CACHE / (
        f"{slugify(song.stem)}-"
        f"{transcript_key(song, model_name, language, lyrics_text, lyrics_source)}.json"
    )

    payload: dict | None = None
    if cache.exists() and not retranscribe:
        try:
            payload = json.loads(cache.read_text(encoding="utf-8"))
            print("  ✓ cached Whisper alignment")
        except Exception:
            payload = None

    if payload is None:
        prompt = lyrics_text[:4000] if lyrics_text else None
        if lyrics_text:
            print(f"  ✓ exact lyrics found: {lyrics_source}")

        actual_language = None if language == "auto" else language
        segments, info = model.transcribe(
            str(song),
            language=actual_language,
            beam_size=1,
            word_timestamps=True,
            vad_filter=False,  # Important for sung vocals.
            condition_on_previous_text=False,
            initial_prompt=prompt,
        )

        payload = {"language": info.language, "segments": []}
        for segment in segments:
            segment_words: list[dict] = []
            for word in segment.words or []:
                text = (word.word or "").strip()
                if not text:
                    continue
                start = float(word.start)
                end = max(float(word.end), start + 0.04)
                segment_words.append(
                    {
                        "text": text,
                        "start": start,
                        "end": end,
                        "probability": float(word.probability or 0.0),
                    }
                )

            payload["segments"].append(
                {
                    "start": float(segment.start),
                    "end": max(float(segment.end), float(segment.start) + 0.04),
                    "text": segment.text.strip(),
                    "words": segment_words,
                }
            )

        cache.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print("  ✓ Whisper timing anchors saved")

    words: list[dict] = []
    for segment in payload.get("segments", []):
        for word in segment.get("words", []):
            text = str(word.get("text", "")).strip()
            if not text:
                continue
            start = float(word["start"])
            words.append(
                {
                    "text": text,
                    "start": start,
                    "end": max(float(word["end"]), start + 0.04),
                }
            )

    if lyrics_text:
        lines, coverage, exact_word_count = align_exact_lyrics(
            lyrics_text,
            words,
            song_duration,
        )
        print(
            f"  ✓ displaying exact lyrics from {lyrics_source} | "
            f"{exact_word_count} authored words | {coverage:.0%} direct Whisper anchors"
        )
        return lines, len(words), lyrics_source, coverage, exact_word_count

    return group_words(words), len(words), None, 0.0, 0

def clean_public(runtime: Path) -> None:
    for subdir in ("audio", "images", "video"):
        directory = runtime / "public" / subdir
        directory.mkdir(parents=True, exist_ok=True)
        for child in directory.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()


def prepare(args) -> tuple[Path, list[dict], Path]:
    from faster_whisper import WhisperModel

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        raise SystemExit(f"Not a directory: {folder}")

    songs = find_files(folder, AUDIO_EXTENSIONS, args.recursive)
    songs = order_audio(folder, songs)
    if not songs:
        supported = ", ".join(sorted(AUDIO_EXTENSIONS))
        raise SystemExit(f"No supported audio files found in {folder}. Supported: {supported}")

    runtime = ensure_runtime()
    clean_public(runtime)

    images = find_files(folder, IMAGE_EXTENSIONS, False)
    videos = find_files(folder, VIDEO_EXTENSIONS, False)

    copied_images: list[Path] = []
    for index, image in enumerate(images):
        dest = runtime / "public" / "images" / f"{index:02d}-{image.name}"
        shutil.copy2(image, dest)
        copied_images.append(dest)

    copied_videos: list[Path] = []
    for index, video in enumerate(videos):
        dest = runtime / "public" / "video" / f"{index:02d}-{video.name}"
        shutil.copy2(video, dest)
        copied_videos.append(dest)

    cover: Path | None = None
    for image in copied_images:
        if "cover" in image.name.lower():
            cover = image
            break
    if cover is None and copied_images:
        cover = copied_images[0]

    print("\n" + "=" * 68)
    print("LYRICVID")
    print("=" * 68)
    print(f"Folder:       {folder}")
    print(f"Songs:        {len(songs)}")
    print(f"Whisper:      {args.model}")
    print(f"Device:       {args.device} / {args.compute_type}")
    print("Music mode:   VAD OFF")
    print("Word timing:  ON")
    print("=" * 68)

    print(f"\nLoading Whisper {args.model} once for the whole folder...")
    model = WhisperModel(
        args.model,
        device=args.device,
        compute_type=args.compute_type,
        cpu_threads=max(1, args.threads),
        num_workers=1,
    )
    print("✓ Whisper loaded")

    manifest: list[dict] = []
    used_slugs: dict[str, int] = {}

    for index, song in enumerate(songs, start=1):
        title = title_for(song)
        base_slug = slugify(title)
        used_slugs[base_slug] = used_slugs.get(base_slug, 0) + 1
        count = used_slugs[base_slug]
        track_slug = base_slug if count == 1 else f"{base_slug}-{count}"

        print(f"\n[{index}/{len(songs)}] {title}")

        audio_dest = runtime / "public" / "audio" / f"{index:02d}-{track_slug}{song.suffix.lower()}"
        shutil.copy2(song, audio_dest)

        duration = audio_duration(song)
        lines, word_count, lyric_source, alignment_coverage, authored_word_count = transcribe_song(
            model,
            song,
            args.model,
            args.language,
            args.retranscribe,
            args.lyrics_source,
            duration,
        )

        background = None
        if copied_videos:
            chosen = copied_videos[(index - 1) % len(copied_videos)]
            background = f"video/{chosen.name}"

        theme = THEMES[(index - 1) % len(THEMES)]
        manifest.append(
            {
                "id": f"Track-{index:02d}-{track_slug}",
                "index": index,
                "slug": track_slug,
                "title": title,
                "audio": f"audio/{audio_dest.name}",
                "cover": f"images/{cover.name}" if cover else None,
                "background": background,
                "duration": duration,
                "theme": theme,
                "lyricsSource": lyric_source,
                "alignmentCoverage": alignment_coverage,
                "authoredWordCount": authored_word_count,
                "lines": lines,
            }
        )

        source_label = lyric_source or "Whisper transcript"
        print(
            f"  ✓ {duration / 60:.2f} min | {word_count} Whisper words | "
            f"{len(lines)} lyric lines | {source_label} | {theme['name']}"
        )
        if duration > 90 and word_count < 50:
            print("  ! Warning: unusually few words were detected for a long song")

    tracks_file = runtime / "src" / "tracks.ts"
    tracks_file.write_text(
        "// AUTO-GENERATED BY LYRICVID\nexport const tracks = "
        + json.dumps(manifest, ensure_ascii=False)
        + ";\n",
        encoding="utf-8",
    )

    return runtime, manifest, folder


def render_tracks(args, runtime: Path, tracks: list[dict], folder: Path) -> None:
    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else folder / "lyric-videos"
    )
    output.mkdir(parents=True, exist_ok=True)

    report = [
        {
            "index": track["index"],
            "title": track["title"],
            "lyricsSource": track.get("lyricsSource") or "whisper",
            "alignmentCoverage": track.get("alignmentCoverage", 0.0),
            "authoredWordCount": track.get("authoredWordCount", 0),
            "lyricLineCount": len(track.get("lines", [])),
        }
        for track in tracks
    ]
    (output / "alignment-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    remotion = runtime / "node_modules" / ".bin" / "remotion"
    if not remotion.exists():
        raise SystemExit("Remotion executable is missing from the runtime")

    print("\n" + "=" * 68)
    print("RENDERING")
    print(f"Output: {output}")
    print("=" * 68)

    for index, track in enumerate(tracks, start=1):
        destination = output / f"{track['slug']}.mp4"
        if destination.exists() and not args.force:
            print(f"[{index}/{len(tracks)}] SKIP existing {destination.name}")
            continue

        print(f"\n[{index}/{len(tracks)}] {track['title']}")
        run(
            [
                str(remotion),
                "render",
                "src/index.ts",
                track["id"],
                str(destination),
                "--codec=h264",
                f"--crf={args.crf}",
                f"--concurrency={args.jobs}",
            ],
            cwd=runtime,
        )

    print("\n" + "=" * 68)
    print("✓ LYRIC VIDEOS COMPLETE")
    print(output)
    print("=" * 68)


def doctor() -> int:
    print(f"LyricVid {__version__}")
    print("=" * 52)
    failures = 0
    for program in ("node", "npm"):
        path = shutil.which(program)
        if path:
            print(f"✓ {program:<8} {path}")
        else:
            print(f"✗ {program:<8} NOT FOUND")
            failures += 1

    print(f"✓ Python   {sys.version.split()[0]}")
    print(f"  Cache    {CACHE_ROOT}")
    print(f"  Runtime  {RUNTIME_ROOT}")
    return failures


def clean_cache() -> None:
    if CACHE_ROOT.exists():
        shutil.rmtree(CACHE_ROOT)
        print(f"Removed {CACHE_ROOT}")
    else:
        print("LyricVid cache is already empty")


def lyrics_info(folder_value: str, recursive: bool, source_policy: str) -> int:
    folder = Path(folder_value).expanduser().resolve()
    if not folder.is_dir():
        raise SystemExit(f"Not a directory: {folder}")

    songs = order_audio(folder, find_files(folder, AUDIO_EXTENSIONS, recursive))
    if not songs:
        raise SystemExit(f"No supported audio files found in {folder}")

    exact_count = 0
    print(f"Lyric sources for {folder}")
    print("=" * 72)
    for song in songs:
        text, source = exact_lyrics(song, source_policy)
        if text:
            exact_count += 1
            words = len([token for token in re.findall(r"\S+", text) if _normalize_alignment_token(token)])
            print(f"✓ {song.name:<36} {source:<24} {words:>5} words")
        else:
            print(f"· {song.name:<36} {'Whisper only':<24}")

    print("=" * 72)
    print(f"Exact authored lyrics: {exact_count}/{len(songs)} tracks")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lyricvid",
        description="Create Whisper-aligned Remotion lyric videos from any music folder.",
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Music folder. Defaults to the current directory.",
    )
    parser.add_argument("--model", default="small.en", help="Whisper model (default: small.en)")
    parser.add_argument("--language", default="en", help="Language code or 'auto' (default: en)")
    parser.add_argument(
        "--lyrics-source",
        choices=["auto", "embedded", "sidecar", "whisper"],
        default="auto",
        help="Lyrics text source. auto prefers embedded metadata, then sidecar files (default: auto)",
    )
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda", "auto"])
    parser.add_argument("--compute-type", default="int8", help="Default: int8; use float16 for CUDA")
    parser.add_argument("--threads", type=int, default=max(1, os.cpu_count() or 4))
    parser.add_argument("--jobs", type=int, default=max(1, min(4, (os.cpu_count() or 4) // 2)))
    parser.add_argument("--crf", type=int, default=24, help="H.264 CRF (default: 24)")
    parser.add_argument("-o", "--output", help="Output directory (default: <music-folder>/lyric-videos)")
    parser.add_argument("--recursive", action="store_true", help="Find audio recursively")
    parser.add_argument("--force", action="store_true", help="Overwrite existing rendered MP4 files")
    parser.add_argument("--retranscribe", action="store_true", help="Ignore cached Whisper transcripts")
    parser.add_argument("--transcribe-only", action="store_true", help="Create/refresh timing data without rendering")
    parser.add_argument("--studio", action="store_true", help="Prepare the folder and open Remotion Studio")
    parser.add_argument("--doctor", action="store_true", help="Check required external dependencies")
    parser.add_argument(
        "--lyrics-info",
        action="store_true",
        help="Show which tracks have embedded/sidecar exact lyrics without transcribing",
    )
    parser.add_argument("--clean-cache", action="store_true", help="Remove LyricVid runtime and transcript caches")
    parser.add_argument("--version", action="version", version=f"lyricvid {__version__}")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.doctor:
        raise SystemExit(doctor())
    if args.clean_cache:
        clean_cache()
        return
    if args.lyrics_info:
        raise SystemExit(lyrics_info(args.folder, args.recursive, args.lyrics_source))

    runtime, tracks, folder = prepare(args)

    if args.transcribe_only:
        print("\n✓ Whisper alignment complete")
        return

    if args.studio:
        remotion = runtime / "node_modules" / ".bin" / "remotion"
        run([str(remotion), "studio", "src/index.ts"], cwd=runtime)
        return

    render_tracks(args, runtime, tracks, folder)


if __name__ == "__main__":
    main()
