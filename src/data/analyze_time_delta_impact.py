from music21 import converter, midi, note


def analyze_midi_file(file_path, output_path):
    """
    Analyzes a MIDI file and modifies empty bars by adding a TIME_DELTA event. Saves the modified MIDI to the specified output path.

    Args:
        file_path (str): The path to the original MIDI file to analyze and modify.
        output_path (str): The path to save the modified MIDI file.

    Returns:
        None

    Raises:
        Exception: If an error occurs during file processing.
    """
    try:
        song = converter.parse(file_path)

        for part_index, part in enumerate(song.parts):
            print(f"Analyzing part {part_index + 1}: {part.partName or 'Unknown'}")

            for measure_index in range(1, 1000):
                measure = part.measure(measure_index)
                if measure is None:
                    break

                try:
                    events = []
                    for note_obj in measure.recurse(classFilter=("Note")):
                        events.append(("NOTE_ON", note_obj.pitch.midi, 4 * note_obj.offset))
                        events.append(
                            ("NOTE_OFF", note_obj.pitch.midi, 4 * note_obj.offset + 4 * note_obj.duration.quarterLength)
                        )

                    bar_data = {"events": events}

                    if not bar_data["events"]:
                        print(f"Empty bar_data in Part {part_index + 1}, Bar {measure_index}")
                        bar_data = {"events": [{"type": "TIME_DELTA", "delta": 4.0}]}
                        measure.append(note.Rest(quarterLength=4.0))

                    else:
                        print(f"Bar {measure_index} Events: {bar_data['events']}")

                except Exception as e:
                    print(f"Error processing part {part_index + 1}, bar {measure_index}: {e}")

        midi_file = midi.translate.music21ObjectToMidiFile(song)
        midi_file.open(output_path, "wb")
        midi_file.write()
        midi_file.close()

        print(f"Modified MIDI file saved to: {output_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


if __name__ == "__main__":
    file_path = "original MIDI file path"
    output_path = "path to save MIDI file with added TIME_DELTA 4.0"

    analyze_midi_file(file_path, output_path)
