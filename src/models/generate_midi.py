"""
Script generates an orchestry enriched file form an input midi file and saves the new file into output path
"""

import os
import argparse
import json
import sys
from pathlib import Path
import note_seq
from src.models.errors import InvalidFileFormatError, UnknownModelError
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
from music21 import converter, tempo, stream
from huggingface_hub import hf_hub_download
from src.AI_GURU.preprocess.music21jsb import preprocess_music21_song
from src.AI_GURU.preprocess.encode import encode_song_data_singular
from src.AI_GURU.token_sequence_helpers import token_sequence_to_note_sequence
from src.models.models_list import models

TOKENIZER_FILENAME = "tokenizer.json"


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

    if not path_to_midi.endswith(".mid"):
        raise InvalidFileFormatError("Input file must be of MIDI format")

    if not os.path.isdir(output_path):
        raise NotADirectoryError(f"The path '{output_path}' is not a valid directory.")


def verify_model(model_name):
    """
    Validates the provided model name against available models.

    Args:
        model_name (str): Name of the model to verify.

    Raises:
        UnknownModelError: If the model name is not in the available models list.
    """
    if not model_name in models.keys():
        raise UnknownModelError(f"{model_name} is not an available model. Available: {models.keys()}")


def combine_note_sequneces(note_sequence1, note_sequence2):
    """
    Overlays two sequences.

    Args:
        note_sequence1 (note_seq.NoteSequence): First note sequence to overlay.
        note_sequence2 (note_seq.NoteSequence): Second note sequence to overlay.

    Returns:
        note_seq.NoteSequence: The combined note sequence.
    """
    combined_sequence = note_seq.NoteSequence()
    combined_sequence.notes.extend(note_sequence1.notes)
    combined_sequence.notes.extend(note_sequence2.notes)

    combined_sequence.total_time = max(note_sequence1.total_time, note_sequence2.total_time)
    combined_sequence.tempos.extend(note_sequence1.tempos or note_sequence2.tempos)

    combined_sequence.notes.sort(key=lambda note: note.start_time)
    return combined_sequence


def generate_midi_score(midi, density, tokenizer_repo, model_repo, max_length=1000, save_tokens=False):
    """
    Generates an enriched MIDI score using the specified model and tokenizer.

    Args:
        midi (str): Path to the input MIDI file.
        density (float): Density parameter for the model.
        tokenizer_repo (str): Hugging Face repository ID for the tokenizer.
        model_repo (str): Hugging Face repository ID for the model.
        max_length (int): Maximum length of the generated sequence. Default is 1000
        save_tokens (boolean): If true, the tokens from original and generated midi get saved in data.json

    Returns:
        note_seq.NoteSequence: The generated note sequence.
    """
    score = converter.parse(midi)
    song_data = preprocess_music21_song(score)
    parsed_midi = encode_song_data_singular(song_data, density)

    repo_type = "model" if tokenizer_repo == model_repo else "dataset"
    tokenizer_path = hf_hub_download(repo_id=tokenizer_repo, filename=TOKENIZER_FILENAME, repo_type=repo_type)
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)
    tokenizer.add_special_tokens({"pad_token": "[PAD]"})

    model = GPT2LMHeadModel.from_pretrained(model_repo)

    input_ids = tokenizer.encode(" ".join(parsed_midi), return_tensors="pt")
    generated_sequence = model.generate(input_ids, max_length=max_length, do_sample=True)
    decoded_sequence = tokenizer.decode(generated_sequence[0])

    generated_note_sequence = token_sequence_to_note_sequence(decoded_sequence, use_program=True, use_drums=True)

    if save_tokens:
        data = {"original": " ".join(parsed_midi), "generated": decoded_sequence}
        with open(os.path.join(".", "data.json"), "w+") as f:
            json.dump(data, f)

    return generated_note_sequence


def generate_orchestrified_midi(midi, density, tokenizer_repo, model_repo, max_length=1000, save_tokens=False):
    """
    Generates an enriched MIDI score and overlays it over the original audio.

    Args:
        midi (str): Path to the input MIDI file.
        density (float): Density parameter for the model.
        tokenizer_repo (str): Hugging Face repository ID for the tokenizer.
        model_repo (str): Hugging Face repository ID for the model.
        max_length (int): Maximum length of the generated sequence. Default is 1000
        save_tokens (boolean): If true, the tokens from original and generated midi get saved in data.json

    Returns:
        note_seq.NoteSequence: The generated note sequence combined with the original audio.
    """
    original_note_sequence = note_seq.midi_io.midi_file_to_note_sequence(midi)
    generated_note_sequence = generate_midi_score(midi, density, tokenizer_repo, model_repo, max_length, save_tokens)

    return combine_note_sequneces(original_note_sequence, generated_note_sequence)


def main():
    parser = argparse.ArgumentParser(description="Generate a MIDI score using a specified model.")
    parser.add_argument("--midi_path", type=str, required=True, help="Path to the MIDI file.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to save the output.")
    parser.add_argument("--model", type=str, required=True, help="Name of the model to use.")
    parser.add_argument("--density", type=float, required=True, help="Density value for generation.")

    args = parser.parse_args()

    midi_path = args.midi_path
    output_path = args.output_path
    model_name = args.model
    density = args.density

    try:
        verify_paths(midi_path, output_path)
        verify_model(model_name)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repos = models[model_name]
    generated_note_sequence = generate_midi_score(midi_path, density, repos["tokenizer"], repos["model"])

    note_seq.note_seq.sequence_proto_to_midi_file(
        generated_note_sequence, os.path.join(output_path, f"{Path(midi_path).stem}_generated.mid")
    )


if __name__ == "__main__":
    main()
