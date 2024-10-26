## Literature Overview

| Title                                             | Year  | Article link                                                             | Source code link                   | Description                   |
|---------------------------------------------------|-------|--------------------------------------------------------------------------|------------------------------------|-------------------------------|
| SingSong                                          | 2023  | https://arxiv.org/abs/2301.12662                                         |                  |             |
| Counterpoint by convolution                       | 2019  | https://arxiv.org/pdf/1903.07227                                         |                  |             |
| MuseGan                                           | 2018  | https://arxiv.org/abs/1709.06298                                         |                  |             |
| MTM-GAN (Literature survey of multi-track music generation) | 2023  | https://doi.org/10.1007/s11227-022-04914-5                               | -                | [see below](#MTM-GAN)            |
| MMM                                               | 2020  | https://arxiv.org/pdf/2008.06048                                         | https://github.com/AI-Guru/MMM-JSB<br>demo: https://jeffreyjohnens.github.io/MMM/ | [see below](#MMM) |
| LakhNES                                           | 2019  | https://arxiv.org/pdf/1907.04868                                         | https://github.com/chrisdonahue/LakhNES<br>demo: https://chrisdonahue.com/LakhNES/| [see below](#LakhNES) |
| A transformer generative adversarial network...   |       | https://ietresearch.onlinelibrary.wiley.com/doi/epdf/10.1049/cit2.12065  |                  |             |
| MuseNet                                           | 2020  | https://www.researchgate.net/publication/363856706_Musenet_Music_Generation_using_Abstractive_and_Generative_Methods | https://github.com/hidude562/OpenMusenet2<br>demo: https://openai.com/index/musenet/  | [see below](#MuseNet)  |

### MuseGan
(Just a few notes for now, as this was described in MuseNet paper)
- 3 different GAN models.
- Can generate different instruments playing in unison.
- Input vector acting as a seed in the netwoek for the different GANs to generate music with the same intent and alignment.
- Lakh Piano-Roll Dataset.

### MTM-GAN
- GAN-based multi-track music generator.
- Generating bass, drums, guitar, piano and strings.
- Mutual game learing of two models: Generative model and Discriminative model.
  - "Minimum-maximum binary game".
  - Training is completed after the Discriminator can no longer distinguish between the real data and the generated data.
- Generetive model generates new data by capturing potential distribution of the actual data.
- Discriminative model is a binary classifier used to determine whether the input is real or generated.
- The formation process of GAN is unstable and can lead to model collaps. Therefore an improved network is proposed consisting of 3 parts:
  - MTM-related model - This component generates distinct tracks for different instruments by capturing correlations between these tracks.
  - Time structure model (For track alignment) - Uses random vectors to manage both independent and interdependent timing for each track.
  - Discritization model - Divides time into units that can capture the different rhythmic requirements for each instrument
- Training on piano rolls generated from MIDI files from LakhMIDI Dataset.
- Includes a Consistency Penalty Term (CT), which adds a regularization layer to the GAN's objective function.
- CT helps stabilize training by reducing large fluctuations in the discriminator’s loss function.
- Track generation:
  - Generate initial outputs for each track individually. Each track’s generator receives input noise and generates sequences that align with specific instrument characteristics.
  - Time structure and MTM correlation model are used to align these tracks.
  - The integrated multi-track output is refined by the discriminator, which iterates with the generator to improve overall coherence.

### MMM
- Based on transformer architecture
- Generating multi-track music
- Non-time-ordered sequence of musical events for each track and concatenate several tracks into a single sequence (taking advantage of attention-mechanism)
  - Important dependencies in the distant history (in their representation the simultaneously sounding notes in different tracks are far apart). Transformer attention mechanism allows distant tokens to be directly attended to if they are relevant to the current prediction.
- Different methods of generation:
  - unconditioned: analogous to generating music from scratch
  - continuation: conditioning the model with musical material that precedes the music to be generated
  - inpainting: conditioning generation on a subset of musical meterial asking the model to fill in the blanks 
  - attribute control: conditioning generation on high-level attributes (style, tempo, density)
- Two main ways in which musical material is represented
  - matrix (pianoroll) - for multi-track material it has a form of a tensor (inherintly inefficient representation)
  - sequence of tokens (each token is a musical event or a piece of metadata)
- By concatenating single-instrument tracks:
  - We can decouple track information, allowing the use of the same `NOTE_ON` and `NOTE_OFF` tokens in each track. This means there are no limitations on the number of tracks that can be represented.
  - We can accomodate a wide veriety of instruments and a large number of tracks without a large token vocabulary.
- Allows for specific attribute control over the instrument for each tract, with guarantee that it will be used.
- Allows for user control regarding note-density for each track.
- Allows for track-level and bar-level inpainting.
- Representation (MultiTrack representation)
  - Single bar:
    - 128 `NOTE_ON`, 128 `NOTE_OFF`, 48 `TIME_SHIFT` tokens
    - each bar begins with `BAR_START` token and ends with `BAR_END` token
  - Track:
    - sequence of bars
    - begins with `TRACK_START` token immediatelly followed by `INSTRUMENT` token, `DENSITY_LEVEL` token and ends with `TRACK_END` token
  - Piece
    - sequence of tracks (but they sound simultaneously)
    - begins with `PIECE_START` token
    - no need for `PIECE_END` token - we can sample until we get n `TRACK_END` tokens for n tracks
  - Model learns to condition the generation of each track on the tracks which precede it.
    - This means that a subset of the musical material can be fixed while generating additional tracks.
    - However, it's impossible to control the musical piece on the bar level (not possible to generate the second bar conditioned on the first, third and fourth)
      - For it to be possible, some bars are replaced with `FILL_PLACEHOLDER` tokens - this representation is called BarFill representation
- Training
  - Lahk MIDI Dataset (Type 1 MIDI)
  - Defined distinct note-density bins for each MIDI instrument
  - Train GPT2 models using HuggingFace Transformers library with 8 attention heads, 6 layersm an embedding of size 512 and attention window of 2048.
  - Trained two typed of models - MMMTrack on MultiTrack representation and MMMBar on BarFill representation. (4-bar and 8-bar versions)
  - Randomly order tracks so that model learns each possible conditional between different tracks.


### LakhNES
- Mutli-instrumental track generator using a Transformer.
- NES-MDB dataset of four-instrumental scores from early video game soud synthesis chip.
- Pretraining with Lakh dataset.
- Capable of generating arbitrarily-long sequences.
- Event-based representation similar to that used for single-instrument music.
  - Each MIDI file is converted to a time-ordered sequence of events, so that every entry in the sequence corresponds to a musical event.
  - Handling of rythmic information - add time shift event wich represent time advancing by some number of ticks
  - 631 events coresponding to time-shifts (3 groups of length) and note on/off events for individual instruments
- Methodology
  - Language modeling factorization - factorize the joint probability of a musical sequence consiting of N events into a product of conditional probabilities. This allows for a simple left-to-right algorithm for music generation (at each timestep sample from model-estimated distribution).
  - The goal of optimization procedure is to find a model configuration which optimizes the likelihood of the real event sequences.
  - Transformer - only concerened with the decoder part.
    - Using Transformer-XL designed specifically to handle longer sequences. In contrast to Trasfomer, it learns how to incorporate recurrent state from previous segments, not only current training segment.
    - 12 attention layers, each with 8 heads. Lr = 2e-5. 30 minibatches of size 30.
  - Pretraining
    - Map each Lakh MIDI file into one that fits the designed representation.
      - Skip the ones that are monophonic melodies, and those that fall outside NES range of MIDI notes.
      - Randomly assign instruments to 3 instruments of NES (P1/P2/TR). There are potentially many possible assignments (variable number of instruments in Lakh files) - outputting multiple examples for one file. 
      - For pervussive instruments each individual percussive voice is assgned to a noise type 
    - Pretrain on such representations.
    - Fine-tune on NES dataset.
  - Each excerpt that is used for training is around 9 seconds long.
- Data augmentation:
  - Transpose melodic voices by random number of semitones.
  - Adjust the speed og the piece by a random percentage.
  - Half of the time remove a random number of instruments from the ensamble.
  - Half of the time shuffle the score-to-instrument alignment for melodic instruments.

### MuseNet
- Model composed of two parts:
  - Discriminator - for generating the first chord of a bar conditioned on the previous bars.
  - Generator - for generating notes of a given bar based on the chord as seed note.
- Generating music bar by bar with contents of each bar conditioned on a chor / set of notes.
- Seed chord chosed from prefixed set of chords using discriminator.
- Details of modules:
  - Discriminator (LSTM):
    - MultiLayerPerceptron
    - 5 layers, 64-32-16-8-8 units in each layer
      - Output layer has 8 units because it's the number of chords it's predicting for a given song.
    - The model can by retrained by replacing the last two layers for a different dataset.
  - Generator (LSTM and GPT2):
    - LSTM architecture (3 layers):
      - Trained using RMSProp as the optimizer.
      - Each layer consists of 3 gates: input, forget and output.
        - Input informs what new information is going to be stored in the cell state.
        - Forget informs what information is to be thrown away.
        - Output provides the activation to the final output of the LSTM block at a given timestamp.
    - Receives the entire hidden vector of the discriminator output.
    - START and END tokens are added to the sequence before feeding it to the decoder.
    - Each recurrent unit of LSTM accepts an element from the hidden vector from the previous units and produces a new hidden element. This is what helps the music sound more coherent.
  - Attention layer (on top of encoder and decoder layers)
    - Learns to conventrate more on parts of the output of the previous layer using the dense output layer. It does so by taking the information from the encoder and weighing it in accordance to the decoder's needs.
- LSTM trained on Lakh Piano roll Dataset.
- GPT2 trained on Nottingham Music Dataset.
