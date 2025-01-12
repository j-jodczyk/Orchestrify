import os
import sys
import mido

# Sometimes, it may be necessary to add the project root to ensure the imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from frechet_music_distance import FrechetMusicDistance
from cut_midi_into_chunks import cut_midi, extract_midi_segment, extract_midi_segment_instrument
from src.models.generate_midi import generate_orchestrified_midi, generate_midi_score
from src.models.models_list import models
from pathlib import Path
import note_seq

root_dir = os.getcwd()

model = "Lakh"

input_directory = os.path.join(root_dir, "data/rock")
output_directory = os.path.join(root_dir, "data/cut/rock")

Path(output_directory).mkdir(parents=True, exist_ok=True)

generated_directory = os.path.join(root_dir, "data/generated/rock")
tokenizer_repo = models[model]["tokenizer"]
model_repo = models[model]["model"]


def validate_midi(file_path):
    try:
        mido.MidiFile(file_path)
        return True  # File is valid
    except Exception as e:
        print(f"Invalid MIDI file: {file_path}. Error: {e}")
        return False


# cut input dataset into 5 sec chunks
for file in os.listdir(input_directory):
    file_path = os.path.join(input_directory, file)
    if validate_midi(file_path):
        extract_midi_segment_instrument(file_path, output_directory)
    else:
        print(f"Skipping invalid file: {file_path}")

# now generate
for file in os.listdir(output_directory):
    # new_midi = generate_midi_score(os.path.join(output_directory, file), 0.9, tokenizer_repo, model_repo)
    new_midi = generate_orchestrified_midi(os.path.join(output_directory, file), 0.9, tokenizer_repo, model_repo)
    with open(os.path.join(generated_directory, file), "w") as fh:
        note_seq.note_seq.sequence_proto_to_midi_file(new_midi, fh.name)

metric = FrechetMusicDistance()
score = metric.score(reference_dataset=output_directory, test_dataset=generated_directory)

with open("fmd_results.txt", "a") as fh:
    fh.write(f"DATASET: {model} SCORE: {score}\n")
