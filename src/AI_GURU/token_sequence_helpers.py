import random
import note_seq

NOTE_LENGTH_16TH_120BPM = 0.25 * 60 / 120
BAR_LENGTH_120BPM = 4.0 * 60 / 120

def get_priming_token_sequence(data_path, stop_on_track_end=None, stop_after_n_tokens=None, return_original=False):

    # Get a random token sequence from the file.
    lines = open(data_path, "r").readlines()
    token_sequence = random.choice(lines)

    result_tokens = []
    track_end_index = 0
    for token_index, token in enumerate(token_sequence.split()):
        result_tokens += [token]

        if stop_on_track_end == track_end_index and token == "TRACK_END":
            break

        if token == "TRACK_END":
            track_end_index += 1

        if stop_after_n_tokens != 0 and token_index + 1 == stop_after_n_tokens:
            break

    result = " ".join(result_tokens)
    if not return_original:
        return result
    else:
        return result, token_sequence

def empty_note_sequence(qpm=120.0, total_time=0.0):
    note_sequence = note_seq.protobuf.music_pb2.NoteSequence()
    note_sequence.tempos.add().qpm = qpm
    note_sequence.ticks_per_quarter = note_seq.constants.STANDARD_PPQ
    note_sequence.total_time = total_time
    return note_sequence

def getDelta(time_delta: str):
    if "/" not in time_delta:
        delta = float(time_delta)
    else:
        # common fraction --> needs to be handled with more care
        num, denom = time_delta.split("/")
        delta = int(num) / int(denom)
    return delta * NOTE_LENGTH_16TH_120BPM

def token_sequence_to_note_sequence(token_sequence, use_program=True, use_drums=True):

    if isinstance(token_sequence, str):
        token_sequence = token_sequence.split()

    note_sequence = empty_note_sequence()
    current_program = 1
    current_is_drum = False
    for token_index, token in enumerate(token_sequence):
        if token == "PIECE_START":
            pass
        elif token == "PIECE_END":
            print("The end.")
            break
        elif token == "TRACK_START":
            current_bar_index = 0
            pass
        elif token == "TRACK_END":
            pass
        elif token.startswith("INST"):
            current_instrument = token.split("=")[-1]
            if current_instrument != "DRUMS" and use_program:
                current_instrument = int(current_instrument)
                current_program = int(current_instrument)
                current_is_drum = False
            if current_instrument == "DRUMS" and use_drums:
                current_instrument = 0
                current_program = 0
                current_is_drum = True
        elif token == "BAR_START":
            current_time = current_bar_index * BAR_LENGTH_120BPM
            current_notes = {}
        elif token == "BAR_END":
            current_bar_index += 1
            pass
        elif token.startswith("NOTE_ON"):
            pitch = int(token.split("=")[-1])
            note = note_sequence.notes.add()
            note.start_time = current_time
            note.end_time = current_time + 4 * NOTE_LENGTH_16TH_120BPM
            note.pitch = pitch
            note.instrument = int(current_instrument)
            note.program = current_program
            note.velocity = 80
            note.is_drum = current_is_drum
            current_notes[pitch] = note
        elif token.startswith("NOTE_OFF"):
            pitch = int(token.split("=")[-1])
            if pitch in current_notes:
                note = current_notes[pitch]
                note.end_time = current_time
        elif token.startswith("TIME_DELTA"):
            delta = getDelta(token.split("=")[-1])
            current_time += delta
        elif token.startswith("DENSITY="):
            pass
        elif (
            token == "[PAD]" or
            token == "[UNK]" or
            token.startswith("FILL")
        ):
            pass
        else:
            assert False, token

    return note_sequence
