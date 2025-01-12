import pretty_midi
import os


def cut_midi(input_path, output_directory):
    input_file = os.path.basename(input_path)
    if os.path.exists(f"{output_directory}/{input_file.split('.')[0]}_fragment_1.mid"):
        # file already was sliced - return
        return
    midi_data = pretty_midi.PrettyMIDI(input_path)
    total_duration = midi_data.get_end_time()

    start_time = 10
    end_time = total_duration - 10

    if end_time <= start_time:
        raise ValueError("MIDI file is too short to process after cutting.")

    current_time = start_time
    fragment_number = 1
    while current_time < end_time:
        fragment_start = current_time
        fragment_end = min(current_time + 5, end_time)

        fragment = midi_data.get_piano_roll(fs=100)
        new_midi = pretty_midi.PrettyMIDI()
        for instrument in midi_data.instruments:
            new_instrument = pretty_midi.Instrument(program=instrument.program, is_drum=instrument.is_drum)
            for note in instrument.notes:
                if fragment_start <= note.start < fragment_end:
                    new_instrument.notes.append(pretty_midi.Note(
                        velocity=note.velocity,
                        pitch=note.pitch,
                        start=max(note.start, fragment_start) - fragment_start,
                        end=min(note.end, fragment_end) - fragment_start
                    ))
            new_midi.instruments.append(new_instrument)

        output_file = f"{output_directory}/{input_file.split('.')[0]}_fragment_{fragment_number}.mid"
        new_midi.write(output_file)
        # print(f"Saved fragment {fragment_number}: {output_file}")

        current_time += 5
        fragment_number += 1


def extract_midi_segment(input_path, output_directory, segment_duration=5):
    input_file = os.path.basename(input_path)
    if os.path.exists(f"{output_directory}/{input_file}"):
        # file already was sliced - return
        return
    midi = pretty_midi.PrettyMIDI(input_file)

    total_duration = midi.get_end_time()

    middle_time = total_duration / 2
    segment_start = max(0, middle_time - segment_duration / 2)
    segment_end = segment_start + segment_duration

    extracted_midi = pretty_midi.PrettyMIDI()

    for instrument in midi.instruments:
        new_instrument = pretty_midi.Instrument(program=instrument.program, is_drum=instrument.is_drum)
        for note in instrument.notes:
            if segment_start <= note.start <= segment_end:
                new_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=max(0, note.start - segment_start),
                    end=max(0, note.end - segment_start)
                )
                new_instrument.notes.append(new_note)
        extracted_midi.instruments.append(new_instrument)

    output_file = f"{output_directory}/{input_file}"
    extracted_midi.write(output_file)
