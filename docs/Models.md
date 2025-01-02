# Training model
The `train_model_from_scratch.py` script contains the code for training a model from scratch. It handles reading the database, parsing, tokenizing, and training the model. This process is crucial for building a robust model using the collected and preprocessed dataset.

:::src.models.train_model_from_scratch

# Transfer learning model
The `train_model_transfer_learning.py` script implements transfer learning for the model. It builds upon a pre-trained model, allowing for faster training and better performance on a smaller dataset or when specialized features need to be added.

:::src.models.train_model_transfer_learning

# Generating midi
To generate midi you can use script in `generate_midi.py`. `generate_midi_score` function is also used in the website backend.

:::src.models.generate_midi

:::src.models.errors