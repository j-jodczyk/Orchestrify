import os
import sys

# Sometimes, it may be necessary to add the project root to ensure the imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import pytest
from music21 import stream, note, meter, tempo, midi
import os
import tempfile
from src.AI_GURU.preprocess.encode import encode_songs_data
from src.AI_GURU.preprocess.preprocessutilities import events_to_events_data
from src.AI_GURU.preprocess.music21jsb import preprocess_music21

def create_test_midi_file():
    """
    Create a simple MIDI file for testing with 5 bars of 4/4 time signature.

    Notes:
        - C4 (MIDI 60)
        - E4 (MIDI 64)
        - G4 (MIDI 67)
        - C5 (MIDI 72)

    Returns:
        str: The file path of the generated MIDI file.
    """
    s = stream.Score()
    part = stream.Part()

    part.append(meter.TimeSignature('4/4'))
    part.append(tempo.MetronomeMark(number=120))

    for i in range(5):
        for pitch in ['C4', 'E4', 'G4', 'C5']:
            part.append(note.Note(pitch, quarterLength=1))

    s.append(part)

    temp_dir = tempfile.gettempdir()
    midi_file_path = os.path.join(temp_dir, "test_midi_file.mid")
    mf = midi.translate.music21ObjectToMidiFile(s)
    mf.open(midi_file_path, 'wb')
    mf.write()
    mf.close()

    return midi_file_path

def test_events_to_events_data():
    """
    Test the events_to_events_data function.

    This function verifies that events are correctly converted into structured data.

    Events:
        A list of tuples representing musical events. Each tuple contains:
        - "NOTE_ON" or "NOTE_OFF" (str): The type of event.
        - pitch (int): The MIDI pitch value.
        - time (float): The time at which the event occurs.

    Expected Output:
        A list of dictionaries representing the structured event data with time deltas preserved.
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

def test_encode_songs_data():
    """
    Test the encode_songs_data function with a test MIDI file.

    This test verifies that the MIDI file is correctly tokenized into sequences.

    Steps:
        1. Create a test MIDI file with 5 bars of predefined notes.
        2. Preprocess the MIDI file to generate song data.
        3. Encode the song data using encode_songs_data.

    Validations:
        - Check that token sequences are generated.
        - Ensure the expected notes (C4, E4, G4, C5) are present in the tokens.
        - Verify the presence of structural tokens (PIECE_START, TRACK_START, etc.).

    Expected Notes:
        - NOTE_ON=60 (C4)
        - NOTE_ON=64 (E4)
        - NOTE_ON=67 (G4)
        - NOTE_ON=72 (C5)
    """
    midi_file_path = create_test_midi_file()

    _, songs_data_valid, _ = preprocess_music21([midi_file_path]) # Due to spliting the dataset for training and validation, when passing only one song the data will be in the songs_data_valid part

    assert len(songs_data_valid) > 0, "Preprocessing should generate songs data."

    transpositions = [0]
    permute = False
    window_size_bars = 2
    hop_length_bars = 1
    density_bins = [1, 2, 3]
    bar_fill = False

    token_sequences = encode_songs_data(
        songs_data_valid, transpositions, permute, window_size_bars, hop_length_bars, density_bins, bar_fill
    )

    expected_notes = ["NOTE_ON=60", "NOTE_ON=64", "NOTE_ON=67", "NOTE_ON=72"]
    for seq in token_sequences:
        for note in expected_notes:
            assert note in seq, f"Expected note {note} not found in token sequence: {seq}"

    assert len(token_sequences) > 0, "Token sequences should not be empty."

    for sequence in token_sequences:
        assert "PIECE_START" in sequence, "Each sequence should start with PIECE_START."
        assert "TRACK_START" in sequence, "Each sequence should contain TRACK_START."
        assert "TRACK_END" in sequence, "Each sequence should contain TRACK_END."
        assert "BAR_START" in sequence, "Each sequence should contain BAR_START."
        assert "BAR_END" in sequence, "Each sequence should contain BAR_END."