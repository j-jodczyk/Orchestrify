from frechet_music_distance import FrechetMusicDistance
from .cut_midi_into_chunks import cut_midi
from src.models.generate_midi import generate_orchestrified_midi
from src.models.models_list import models
import os
from pathlib import Path
import note_seq

root_dir = os.getcwd()

model = "Lakh"

input_directory = os.path.join(root_dir, "data/rock")
output_directory = os.path.join(root_dir, "data/cut/rock")

Path(output_directory).mkdir(parents=True, exist_ok=True)

generated_directory = os.path.join(root_dir, "data/generated/rock")
tokenizer_repo =  models[model]["tokenizer"]
model_repo = models[model]["model"]

# cut input dataset into 5 sek chunks
for file in os.listdir(input_directory):
    cut_midi(os.path.join(input_directory, file), output_directory)

# now generate
for file in os.listdir(output_directory):
    new_midi = generate_orchestrified_midi(os.path.join(output_directory, file), 0.9, tokenizer_repo, model_repo)
    with open(os.path.join(generated_directory, file), "w") as fh:
        note_seq.note_seq.sequence_proto_to_midi_file(new_midi, f"/{fh.name}")

metric = FrechetMusicDistance()
score = metric.score(
    reference_dataset=output_directory,
    test_dataset=generated_directory
)

with open('fmd_results.txt', 'a') as fh:
    fh.write(f'DATASET: {model} SCORE: {score}\n')
