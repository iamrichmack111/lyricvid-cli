from mutagen.id3 import ID3, USLT

from lyricvid.cli import align_exact_lyrics, embedded_lyrics, exact_lyrics, lyrics_from_tags


def test_extracts_id3_uslt_exact_lyrics():
    tags = ID3()
    tags.add(
        USLT(
            encoding=3,
            lang="eng",
            desc="",
            text="Set FACL on the file\nTerraform maps the kingdom",
        )
    )
    text, source = lyrics_from_tags(tags)
    assert text == "Set FACL on the file\nTerraform maps the kingdom"
    assert source == "embedded:USLT"


def test_exact_alignment_preserves_authored_spelling_and_lines():
    lyrics = "Set FACL on the file.\nTShark maps the network."
    whisper_words = [
        {"text": "Set", "start": 1.0, "end": 1.2},
        {"text": "facl", "start": 1.2, "end": 1.5},
        {"text": "on", "start": 1.5, "end": 1.7},
        {"text": "the", "start": 1.7, "end": 1.9},
        {"text": "file", "start": 1.9, "end": 2.2},
        {"text": "t", "start": 3.0, "end": 3.1},
        {"text": "shark", "start": 3.1, "end": 3.4},
        {"text": "maps", "start": 3.4, "end": 3.7},
        {"text": "the", "start": 3.7, "end": 3.9},
        {"text": "network", "start": 3.9, "end": 4.3},
    ]

    lines, coverage, authored_count = align_exact_lyrics(
        lyrics,
        whisper_words,
        song_duration=10.0,
    )

    assert authored_count == 9
    assert lines[0]["text"] == "Set FACL on the file."
    assert lines[1]["text"] == "TShark maps the network."
    assert [w["text"] for w in lines[0]["words"]] == ["Set", "FACL", "on", "the", "file."]
    assert [w["text"] for w in lines[1]["words"]] == ["TShark", "maps", "the", "network."]
    assert coverage > 0.5
    for line in lines:
        for word in line["words"]:
            assert word["end"] > word["start"]


def test_whisper_policy_ignores_metadata(tmp_path, monkeypatch):
    fake = tmp_path / "song.mp3"
    fake.write_bytes(b"not-an-audio-file")
    monkeypatch.setattr("lyricvid.cli.embedded_lyrics", lambda song: ("Exact words", "embedded:USLT"))
    assert exact_lyrics(fake, "whisper") == (None, None)


def test_embedded_lyrics_reads_id3_file(tmp_path):
    path = tmp_path / "song.mp3"
    tags = ID3()
    tags.add(USLT(encoding=3, lang="eng", desc="", text="Exact metadata line"))
    tags.save(path)
    assert embedded_lyrics(path) == ("Exact metadata line", "embedded:USLT")


def test_lrc_timestamps_are_not_rendered():
    lines, _, _ = align_exact_lyrics(
        "[00:01.00]Exact first line\n[00:03.25]Exact second line",
        [
            {"text": "Exact", "start": 1.0, "end": 1.2},
            {"text": "first", "start": 1.2, "end": 1.5},
            {"text": "line", "start": 1.5, "end": 1.8},
            {"text": "Exact", "start": 3.25, "end": 3.5},
            {"text": "second", "start": 3.5, "end": 3.8},
            {"text": "line", "start": 3.8, "end": 4.0},
        ],
        5.0,
    )
    assert [line["text"] for line in lines] == ["Exact first line", "Exact second line"]
