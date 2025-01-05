"""
Contains script to generate a MIDI file from a model.
"""

import note_seq
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
from src.AI_GURU.token_sequence_helpers import (
    get_priming_token_sequence,
    token_sequence_to_note_sequence,
)


def generate_midi(
    model,
    tokenizer,
    validation_data_path,
    output_file,
    max_length=1000,
    temperature=0.9,
):
    """
    Generates a MIDI file from a given model and tokenizer using a priming sequence.

    Args:
        model (GPT2LMHeadModel): The pre-trained language model to generate sequences.
        tokenizer (PreTrainedTokenizerFast): The tokenizer corresponding to the model.
        validation_data_path (str): Path to the validation data file containing token sequences.
        output_file (str): Path where the generated MIDI file will be saved.
        max_length (int): Maximum length of the generated sequence. Default is 1000.
        temperature (float): Sampling temperature for generation. Default is 0.9.
    """
    priming_sample, priming_sample_original = get_priming_token_sequence(
        validation_data_path,
        stop_on_track_end=0,
        stop_after_n_tokens=20,
        return_original=True,
    )

    input_ids = tokenizer.encode(priming_sample, return_tensors="pt")

    generated_sequence = model.generate(
        input_ids,
        max_length=max_length,
        temperature=temperature,
    )

    decoded_sequence = tokenizer.decode(generated_sequence[0])
    note_sequence = token_sequence_to_note_sequence(decoded_sequence, use_program=False, use_drums=True)

    note_seq.sequence_proto_to_midi_file(note_sequence, output_file)
    print(f"Generated MIDI file saved to {output_file}")


if __name__ == "__main__":
    model_path = "Milos121/MMM_jsb_mmmbar"
    tokenizer_path = "../data/external/Jazz Midi/jsb_mmmtrack/tokenizer.json"
    validation_data_path = "../../data/external/Jazz Midi/jsb_mmmtrack/token_sequences_valid.txt"
    output_file = "generated_music.mid"

    model = GPT2LMHeadModel.from_pretrained(model_path)
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)

    generate_midi(
        model=model,
        tokenizer=tokenizer,
        validation_data_path=validation_data_path,
        output_file=output_file,
        max_length=1000,
        temperature=0.9,
    )
