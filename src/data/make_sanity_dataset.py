from music21 import note, chord, stream, instrument
from pathlib import Path
import os


def create_midi_with_instruments(notes_and_durations, filepath, inst=None, is_drum=False):
    """
    Creates a MIDI file from an array of (note, duration) tuples with optional instrument assignment.

    Args:
        notes_and_durations: List of tuples where each tuple is (pitch, duration).
            - pitch: A string for pitched notes (e.g., 'C4'), an int for MIDI drums (e.g., 36),
              or None for a rest.
            - duration: A float representing the quarter note length.
        filename: The name of the output MIDI file.
        inst: An instance of a music21.instrument (e.g., instrument.Piano()).
        is_drum: If True, creates a drum track on MIDI channel 10.
    """
    s = stream.Stream()
    if inst:
        s.insert(0, inst)

    for pitch, duration in notes_and_durations:
        if pitch is None:
            s.append(note.Rest(quarterLength=duration))
        elif isinstance(pitch, list):  # Chord
            s.append(chord.Chord(pitch, quarterLength=duration))
        elif isinstance(pitch, int) and is_drum:
            drum_note = note.Unpitched(pitch, quarterLength=duration)
            drum_note.storedInstrument = instrument.Woodblock()  # Default drum instrument
            s.append(drum_note)
        else:
            s.append(note.Note(pitch, quarterLength=duration))

    if is_drum:
        for element in s.notes:
            if isinstance(element, note.Unpitched):
                element.channel = 9

    s.write("midi", fp=filepath)


def main():
    project_root = Path(__file__).resolve().parent.parent.parent
    output_dir = project_root / "data/sanity"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_midi = [
        ([("C4", 4)], "single_tone.mid", instrument.Piano()),
        (
            [(pitch, 1) for pitch in ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]],
            "ascending_major_scale.mid",
            instrument.Flute(),
        ),
        ([(["C4", "E4", "G4"], 2)], "c_major_triad.mid", instrument.AcousticGuitar()),
        (
            [(["C4", "E4", "G4"], 2), (["F4", "A4", "C5"], 2), (["G4", "B4", "D5"], 2), (["C4", "E4", "G4"], 2)],
            "chord_progression.mid",
            instrument.AcousticGuitar(),
        ),
        (
            [
                ("C4", 1),
                ("C4", 1),
                ("G4", 1),
                ("G4", 1),
                ("A4", 1),
                ("A4", 1),
                ("G4", 2),
                (None, 1),  # Rest
                ("F4", 1),
                ("F4", 1),
                ("E4", 1),
                ("E4", 1),
                ("D4", 1),
                ("D4", 1),
                ("C4", 2),
            ],
            "twinkle_twinkle.mid",
            instrument.Piano(),
        ),
        (
            [(pitch, 1) for pitch in ["C5", "B4", "A4", "G4", "F4", "E4", "D4", "C4"]],
            "descending_major_scale.mid",
            instrument.Piano(),
        ),
        ([(["C4", "Eb4", "G4"], 2)], "c_minor_triad.mid", instrument.Piano()),
        (
            [("C4", 0.5), ("E4", 0.5), ("G4", 0.5), ("C5", 0.5), ("G4", 0.5), ("E4", 0.5), ("C4", 0.5)],
            "arpeggio.mid",
            instrument.Violin(),
        ),
        ([(pitch, 1) for pitch in ["C4", "D4", "E4", "G4", "A4", "C5"]], "pentatonic_scale.mid", instrument.Piano()),
        (
            [
                (["C4", "E4", "G4"], 1),  # Chord
                ("C4", 0.5),
                ("C4", 0.5),  # Bass Notes
                (["F4", "A4", "C5"], 1),
                ("F4", 0.5),
                ("F4", 0.5),
                (["G4", "B4", "D5"], 1),
                ("G4", 0.5),
                ("G4", 0.5),
            ],
            "waltz.mid",
            instrument.Piano(),
        ),
        (
            [("C4", 0.75), (None, 0.25), ("E4", 0.5), ("G4", 1), ("C5", 0.75), (None, 0.25), ("G4", 0.5), ("E4", 1)],
            "syncopated_rhythm.mid",
            instrument.Piano(),
        ),
    ]

    for notes, filename, instr in test_midi:
        filepath = output_dir / filename
        create_midi_with_instruments(notes, filepath, instr)

    test_midi_drums = [
        (
            [(36, 1), (42, 1), (38, 1), (42, 1), (36, 1), (42, 1), (38, 1), (42, 1)],  # Kick, Hi-Hat, Snare, Hi-Hat
            "basic_rock_beat.mid",
            None,
            True,
        ),
        (
            [(36, 1), (42, 0.5), (46, 0.5), (38, 0.75), (42, 0.25), (36, 0.5), (42, 0.5), (38, 1)],
            "funky_beat.mid",
            None,
            True,
        ),
        ([(38, 0.125) for _ in range(32)], "drum_roll.mid", None, True),  # 32 notes for a drum roll
        (
            [
                (42, 0.25),
                (42, 0.25),
                (42, 0.25),
                (42, 0.25),  # Closed Hi-Hat
                (46, 0.5),
                (42, 0.25),
                (42, 0.25),
                (42, 0.25),
                (42, 0.25),  # Open Hi-Hat
            ],
            "hi_hat_groove.mid",
            None,
            True,
        ),
    ]

    for notes, filename, instr, is_drums in test_midi_drums:
        filepath = output_dir / filename
        create_midi_with_instruments(notes, filepath, instr, is_drums)


if __name__ == "__main__":
    main()
