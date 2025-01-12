import os
import sys
import tempfile
import pytest
from music21 import stream, note, meter, tempo, midi

# Add project root to the path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.AI_GURU.preprocess.encode import encode_songs_data
from src.AI_GURU.preprocess.preprocessutilities import events_to_events_data
from src.AI_GURU.preprocess.music21jsb import preprocess_music21


def create_midi_file_with_notes(notes_per_bar, num_bars, filename):
    """
    Helper function to create a MIDI file with a given number of bars and notes per bar.
    """
    score = stream.Score()
    part = stream.Part()

    part.append(meter.TimeSignature("4/4"))
    part.append(tempo.MetronomeMark(number=120))

    for _ in range(num_bars):
        for pitch in notes_per_bar:
            part.append(note.Note(pitch, quarterLength=1))

    score.append(part)

    midi_file_path = os.path.join(tempfile.gettempdir(), filename)
    mf = midi.translate.music21ObjectToMidiFile(score)
    mf.open(midi_file_path, "wb")
    mf.write()
    mf.close()

    return midi_file_path


def create_test_midi_file():
    """
    Create a simple MIDI file for testing with 5 bars of 4/4 time signature.
    """
    return create_midi_file_with_notes(["C4", "E4", "G4", "C5"], 5, "test_midi_file.mid")


def create_midi_with_empty_and_filled_bars():
    """
    Create a MIDI file with a mix of empty and filled bars for testing.
    """
    score = stream.Score()
    part = stream.Part()

    part.append(meter.TimeSignature("4/4"))
    part.append(tempo.MetronomeMark(number=120))

    # Bar with notes
    filled_bar = stream.Measure(number=1)
    for pitch in ["C4", "E4", "G4", "C5"]:
        filled_bar.append(note.Note(pitch, quarterLength=1))
    part.append(filled_bar)

    # Empty bar
    empty_bar = stream.Measure(number=2)
    empty_bar.append(note.Rest(quarterLength=4))
    part.append(empty_bar)

    # Another bar with notes
    another_filled_bar = stream.Measure(number=3)
    for pitch in ["D4", "F4", "A4", "D5"]:
        another_filled_bar.append(note.Note(pitch, quarterLength=1))
    part.append(another_filled_bar)

    score.append(part)

    midi_file_path = os.path.join(tempfile.gettempdir(), "test_midi_with_mixed_bars.mid")
    mf = midi.translate.music21ObjectToMidiFile(score)
    mf.open(midi_file_path, "wb")
    mf.write()
    mf.close()

    return midi_file_path


def test_events_to_events_data():
    """
    Test the events_to_events_data function.
    """
    events = [
        ("NOTE_ON", 60, 0.0),
        ("NOTE_OFF", 60, 1.0),
        ("NOTE_ON", 64, 1.0),
        ("NOTE_OFF", 64, 2.0),
    ]

    expected_events_data = [
        {"type": "NOTE_ON", "pitch": 60},
        {"type": "TIME_DELTA", "delta": 1.0},
        {"type": "NOTE_OFF", "pitch": 60},
        {"type": "NOTE_ON", "pitch": 64},
        {"type": "TIME_DELTA", "delta": 1.0},
        {"type": "NOTE_OFF", "pitch": 64},
    ]

    result = events_to_events_data(events)
    assert result == expected_events_data


def test_events_to_events_data_on_empty_and_filled_bars():
    """
    Test the events_to_events_data function with a MIDI file containing empty and filled bars.
    """
    midi_file_path = create_midi_with_empty_and_filled_bars()

    _, songs_data_valid, _ = preprocess_music21([midi_file_path])

    assert len(songs_data_valid) > 0, "Preprocessing should generate songs data."

    expected_events_data = [
        {
            "title": None,
            "number": None,
            "tracks": [
                {
                    "name": None,
                    "number": 0,
                    "bars": [
                        {
                            "events": [
                                {"type": "NOTE_ON", "pitch": 60},
                                {"type": "TIME_DELTA", "delta": 4.0},
                                {"type": "NOTE_OFF", "pitch": 60},
                                {"type": "NOTE_ON", "pitch": 64},
                                {"type": "TIME_DELTA", "delta": 4.0},
                                {"type": "NOTE_OFF", "pitch": 64},
                                {"type": "NOTE_ON", "pitch": 67},
                                {"type": "TIME_DELTA", "delta": 4.0},
                                {"type": "NOTE_OFF", "pitch": 67},
                                {"type": "NOTE_ON", "pitch": 72},
                                {"type": "TIME_DELTA", "delta": 4.0},
                                {"type": "NOTE_OFF", "pitch": 72},
                            ]
                        },
                        {"events": [{"type": "TIME_DELTA", "delta": 16.0}]},
                        {
                            "events": [
                                {"type": "NOTE_ON", "pitch": 62},
                                {"type": "TIME_DELTA", "delta": 4.0},
                                {"type": "NOTE_OFF", "pitch": 62},
                                {"type": "NOTE_ON", "pitch": 65},
                                {"type": "TIME_DELTA", "delta": 4.0},
                                {"type": "NOTE_OFF", "pitch": 65},
                                {"type": "NOTE_ON", "pitch": 69},
                                {"type": "TIME_DELTA", "delta": 4.0},
                                {"type": "NOTE_OFF", "pitch": 69},
                                {"type": "NOTE_ON", "pitch": 74},
                                {"type": "TIME_DELTA", "delta": 4.0},
                                {"type": "NOTE_OFF", "pitch": 74},
                            ]
                        },
                    ],
                }
            ],
        }
    ]

    assert songs_data_valid == expected_events_data, "Songs data validation failed."


def validate_token_sequences(token_sequences, expected_notes, expected_structural_tokens):
    """
    Helper function to validate token sequences for common checks.
    """
    assert len(token_sequences) > 0, "Token sequences should not be empty."

    for sequence in token_sequences:
        for note in expected_notes:
            assert note in sequence, f"Expected note {note} not found in token sequence: {sequence}"

        for token in expected_structural_tokens:
            assert token in sequence, f"Expected structural token {token} not found in sequence: {sequence}"


def test_encode_songs_data():
    """
    Test the encode_songs_data function with a test MIDI file.
    """
    midi_file_path = create_test_midi_file()

    _, songs_data_valid, _ = preprocess_music21([midi_file_path])
    assert len(songs_data_valid) > 0, "Preprocessing should generate songs data."

    token_sequences = encode_songs_data(
        songs_data_valid,
        transpositions=[0],
        permute=False,
        window_size_bars=2,
        hop_length_bars=1,
        density_bins=[1, 2, 3],
        bar_fill=False,
    )

    expected_notes = ["NOTE_ON=60", "NOTE_ON=64", "NOTE_ON=67", "NOTE_ON=72"]
    expected_structural_tokens = ["PIECE_START", "TRACK_START", "TRACK_END", "BAR_START", "BAR_END"]

    validate_token_sequences(token_sequences, expected_notes, expected_structural_tokens)


def test_encode_songs_data_on_empty_bars():
    """
    Test the encode_songs_data function with a MIDI file containing empty and filled bars.
    """
    midi_file_path = create_midi_with_empty_and_filled_bars()

    _, songs_data_valid, _ = preprocess_music21([midi_file_path])
    assert len(songs_data_valid) > 0, "Preprocessing should generate songs data."

    token_sequences = encode_songs_data(
        songs_data_valid,
        transpositions=[0],
        permute=False,
        window_size_bars=2,
        hop_length_bars=1,
        density_bins=[1, 2, 3],
        bar_fill=False,
    )

    # We are not checking for third bar notes, because they will not be included in the token_sequences due to how get_bar_indices function defines sliding windows
    expected_notes = ["NOTE_ON=60", "NOTE_ON=64", "NOTE_ON=67", "NOTE_ON=72", "TIME_DELTA=16.0"]
    expected_structural_tokens = ["PIECE_START", "TRACK_START", "TRACK_END", "BAR_START", "BAR_END"]

    validate_token_sequences(token_sequences, expected_notes, expected_structural_tokens)
