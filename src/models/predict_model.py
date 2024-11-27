"""
Contains script to generate midi file from a model
"""
import note_seq
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
from src.AI_GURU.token_sequence_helpers import get_priming_token_sequence, token_sequence_to_note_sequence

# todo: this should not be main function, but rather a parametrized function that will take model and tokenizer
def main():
    model_path = "Milos121/MMM_jsb_mmmbar"
    tokenizer_path = '../data/external/Jazz Midi/jsb_mmmtrack/tokenizer.json'

    model = GPT2LMHeadModel.from_pretrained(model_path)
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)

    validation_data_path = '../../data/external/Jazz Midi/jsb_mmmtrack/token_sequences_valid.txt'
    # with current settings this retrieves the first track from the encoded sequence.
    priming_sample, priming_sample_original = get_priming_token_sequence(
        validation_data_path,
        stop_on_track_end=0,
        stop_after_n_tokens=20,
        return_original=True
    )

    input_ids = tokenizer.encode(priming_sample, return_tensors="pt")

    generated_sequence = model.generate(
        input_ids,
        max_length=1000,
        temperature=0.9,
    )

    decoded_sequence = tokenizer.decode(generated_sequence[0])
    note_sequence = token_sequence_to_note_sequence(decoded_sequence, use_program=False, use_drums=True)

    note_seq.play_sequence(note_sequence)

    # todo: instead of playing, we should be saving output to file
