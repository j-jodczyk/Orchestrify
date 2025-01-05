# Training model
The `train_model_from_scratch.py` script implements model training from scratch, without utilizing pre-trained weights or models.

:::src.models.train_model_from_scratch

# Transfer learning model
The `train_model_transfer_learning.py` script implements transfer learning for the model. It builds upon a pre-trained model, allowing for faster training and better performance on a smaller dataset.

:::src.models.train_model_transfer_learning

# Generating midi
To generate midi you can use script in `generate_midi.py`. `generate_midi_score` function is also used in the website backend.

:::src.models.generate_midi

:::src.models.errors