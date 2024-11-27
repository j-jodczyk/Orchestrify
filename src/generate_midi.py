"""
Script generates an orchestry enriched file form an input midi file and saves the new file into output path
"""

import os
import json
import note_seq
from errors import InvalidFileFormatError, UnknownModelError
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
from music21 import converter, tempo, stream
from AI_GURU.preprocess.music21jsb import preprocess_music21_song
from AI_GURU.preprocess.encode import encode_song_data_singular
from AI_GURU.token_sequence_helpers import token_sequence_to_note_sequence


model_name_mapping = {
    "Bach_Horale": "Milos121/MMM_jsb_mmmbar",
}

# todo: this will have to be resolved - should one tokenizer be universal for all datasets - I got different results from two :/
# for the final project we will most probably load them to hf
# TODO: this is absolute path :/
tokenizer_path = "/home/julia/WIMU/Orchestrify/data/external/Jazz Midi/jsb_mmmtrack/tokenizer.json"

def verify_paths(path_to_midi, output_path):
    """
    Verifies that:
    - path_to_midi is a valid midi file
    - output_path is a valid directory.

    Args:
        path_to_midi (str): Path to the MIDI file.
        output_path (str): Path to the output directory.

    Raises:
        FileNotFoundError: If the MIDI file does not exist.
        InvalidFileFormatError: If the provided file is not MIDI.
        NotADirectoryError: If the output path is not a directory.
    """
    if not os.path.isfile(path_to_midi):
        raise FileNotFoundError(f"The midi file at path '{path_to_midi}' does not exist.")

    if not path_to_midi.endswith('.mid'):
        raise InvalidFileFormatError("Input file must be of MIDI format")

    if not os.path.isdir(output_path):
        raise NotADirectoryError(f"The path '{output_path}' is not a valid directory.")

def verify_model(model_name):
    if not model_name in model_name_mapping.keys():
        raise UnknownModelError(f"{model_name} is not an available model. Available: {model_name_mapping.keys()}")


def get_end_time(score):
    """
    TODO: there is a bug in this implementation (or maybe more accurate would be to say: there is a bug in the logic of it) - I don't think it works correctly
    """
    bpm = 120
    for element in score.flat:
        if isinstance(element, tempo.MetronomeMark):
            bpm = element.number
            break

    seconds = 5
    mps = bpm / (60 * 4) # for 4/4 tempo
    return int(mps * seconds)

def trim(score, start_time, end_time):
    """
    Trims the measures of the midi file
    """
    return score.measures(start_time, end_time)

def get_trimmed_instrument_score(score, picked_instrument_name=None):
    """
    Separates the single instrument score from the midi file and trims it to be 5 seconds long

    # TODO: time should not be hard coded
    """
    instrument_score = stream.Score()
    instrument_score.metadata = score.metadata

    end_time = get_end_time(score)

    if not picked_instrument_name:
        instrument_score.append(trim(score.parts[0], 0, end_time))

    for part in score.parts:
        if part.getInstrument().instrumentName == picked_instrument_name:
            instrument_score.append(trim(part, 0, end_time))

    return instrument_score

def get_instrument_list(score):
    """
    Retrives the list of instruments from midi file
    """
    return [score.parts[i].getInstrument() for i in range(len(score.parts))]

def main():
    with open('./src/generate_midi.json', 'r') as file: #TODO: relative path
        config = json.load(file)

    midi_path = config["midi_path"]
    output_path = config["output_path"]
    model_name = config["model"]
    density = config["density"]

    try:
        verify_paths(midi_path, output_path)
        verify_model(model_name)
    except (Exception) as e:
        print(f"Error: {e}")
        exit(1)

    score = converter.parse(midi_path)

    instrument_list = get_instrument_list(score)
    instrument = None
    if len(instrument_list) > 1:
        instrument_list_str = '\n'.join([i.instrumentName for i in instrument_list if i != None])
        print(f"Provided midi file has more than one instrument. Please choose the one to use as base for generation:\n{instrument_list_str}")
        while instrument is None or instrument not in instrument_list_str:
            instrument = input(">")

    instrument_score = get_trimmed_instrument_score(score, instrument)
    song_data = preprocess_music21_song(instrument_score, False)
    parsed_midi = encode_song_data_singular(song_data, density)

    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})
    model = GPT2LMHeadModel.from_pretrained(model_name_mapping[model_name])

    input_ids = tokenizer.encode(' '.join(parsed_midi), return_tensors="pt")
    generated_sequence = model.generate(
        input_ids,
        max_length=1000,
        temperature=0.5,
    )
    decoded_sequence = tokenizer.decode(generated_sequence[0])

    data = {
        "original": ' '.join(parsed_midi),
        "generated": decoded_sequence
    }

    with open(os.path.join(output_path, 'data.json'), 'w+') as f:
        json.dump(data, f)


    # Save both original and generated
    original_note_squence = token_sequence_to_note_sequence(' '.join(parsed_midi), use_program=True, use_drums=True)
    generated_note_sequence = token_sequence_to_note_sequence(decoded_sequence, use_program=True, use_drums=True)
    note_seq.note_seq.sequence_proto_to_midi_file(generated_note_sequence, os.path.join(output_path, "generated.mid"))
    note_seq.note_seq.sequence_proto_to_midi_file(original_note_squence, os.path.join(output_path, "original.mid"))


if __name__ == "__main__":
    main()
