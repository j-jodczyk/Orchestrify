## Literature Overview

| Title                                             | Year  | Article link                                                             | Source code link                   | Description                   |
|---------------------------------------------------|-------|--------------------------------------------------------------------------|------------------------------------|-------------------------------|
| SingSong                                          | 2023  | https://arxiv.org/abs/2301.12662                                         |                  | [see below](#SingSong) |
| Counterpoint by convolution                       | 2019  | https://arxiv.org/pdf/1903.07227                                         |                  | [see below](#Counterpoint-by-convolution) |
| MuseGan                                           | 2018  | https://arxiv.org/abs/1709.06298                                         |                  | [see below](#MuseGAN) |
| MTM-GAN (Literature survey of multi-track music generation) | 2023  | https://doi.org/10.1007/s11227-022-04914-5                               | -                | [see below](#MTM-GAN)            |
| MMM                                               | 2020  | https://arxiv.org/pdf/2008.06048                                         | https://github.com/AI-Guru/MMM-JSB<br>demo: https://jeffreyjohnens.github.io/MMM/ | [see below](#MMM) |
| LakhNES                                           | 2019  | https://arxiv.org/pdf/1907.04868                                         | https://github.com/chrisdonahue/LakhNES<br>demo: https://chrisdonahue.com/LakhNES/| [see below](#LakhNES) |
| A transformer generative adversarial network...   |       | https://ietresearch.onlinelibrary.wiley.com/doi/epdf/10.1049/cit2.12065  |                  |             |
| MuseNet                                           | 2020  | https://www.researchgate.net/publication/363856706_Musenet_Music_Generation_using_Abstractive_and_Generative_Methods | https://github.com/hidude562/OpenMusenet2<br>demo: https://openai.com/index/musenet/  | [see below](#MuseNet)  |
| Music Transformer                                 | 2018  | https://arxiv.org/abs/1809.04281                                         |                  | [see below](#music-transformer) |
| Anticipatory Music Transformer                    | 2023  | https://arxiv.org/abs/2306.08620                                         | https://github.com/jthickstun/anticipation | [see below](#anticipatory-music-transformer) |

### SingSong
- Based on conditional generative modeling: Utilizes AudioLM as a foundational model but adapts it for generating instrumental music that aligns with vocal inputs.
- Generating instrumental accompaniments from vocal inputs: Directly uses a user's singing or humming to create synchronized instrumental accompaniments, enabling seamless mixing.
  - Key innovation involves aligning input vocals with instrumental accompaniment, allowing naive mixing while preserving coherence.
- Training and data preparation:
  - Source separation for dataset creation: A state-of-the-art source separation algorithm (MDXNet) is used to create aligned pairs of vocals and instrumentals from a large dataset of 1M music tracks. This serves as parallel training data.
  - Training on audio codes: Instead of modeling raw waveforms, SingSong leverages AudioLM's hierarchical representation of audio via discrete codes (semantic and acoustic). This enables scalable training and generation of high-quality audio.
- Featurization and conditioning:
  - Adding noise to vocals: To address artifacts in separated vocals, noise is introduced to mask residual instrumental sounds. This step improves the model’s generalization ability to real-world isolated vocals.
- Model architecture:
  - A sequence-to-sequence Transformer model (based on T5 architecture) is used for predicting instrumental audio codes from vocal features.
  - Coarse and fine levels of audio representation are generated hierarchically to improve fidelity.
- Evaluation and performance:
  - Frechet Audio Distance (FAD) is used as a primary metric to evaluate audio quality and generalization, showing a 55% improvement with advanced featurizations.
  - Listening study results indicate a significant preference for SingSong-generated instrumentals compared to baseline retrieval-based methods.
- Application and user impact:
  - Allows users to create personalized music tracks by singing or humming, expanding creative possibilities for both musicians and non-musicians.

### Counterpoint by convolution
- Nonlinear music composition: COCONET uses a convolutional neural network (CNN) to model counterpoint by allowing flexible, non-chronological composition and revision, mimicking human composers' approach.
- The model leverages an orderless NADE framework to predict notes without adhering to a fixed order, enabling complex polyphonic structures.
- Uses blocked Gibbs sampling to iteratively refine and correct generated notes, improving overall sample quality and coherence.
- Encodes music as three-dimensional tensors (piano rolls), capturing both local and global structures of polyphonic pieces, particularly Bach chorales.
- Demonstrates superior sample quality through both quantitative metrics and human evaluations, outperforming traditional autoregressive models in generating coherent Bach-style counterpoint.
- Supports diverse applications like harmonization and polyphonic completion, enabling creative exploration of musical structures.

### MuseGAN
- **Overview**: MuseGAN is a GAN-based model designed for generating multi-track, polyphonic symbolic music. It focuses on generating music with harmonic and rhythmic structure, multi-track interdependency, and temporal coherence.
- **Model Variants**:
  - **Jamming Model**: Uses multiple generators and discriminators, each responsible for a separate track, allowing for independent track generation.
  - **Composer Model**: Uses a single generator and a single discriminator to generate multi-track piano-rolls collectively. It aims to harmonize the tracks together.
  - **Hybrid Model**: Combines elements of the Jamming and Composer models, utilizing separate generators for each track but with shared input to encourage inter-track coordination.
- **Data Representation**: Multi-track piano-roll representation of polyphonic music, where each track corresponds to a different instrument (e.g., bass, drums, guitar, piano, and strings).
- **Training Dataset**:
  - **Lakh Pianoroll Dataset (LPD)**: Derived from the Lakh MIDI Dataset (LMD). Includes 173,997 unique multi-track piano-rolls, reduced to five core tracks.
  - The dataset was cleansed and segmented into phrases of four bars for training.
- **Training Strategy**:
  - Utilizes Wasserstein GAN with a gradient penalty (WGAN-GP) to stabilize training and reduce mode collapse.
  - The generator consists of two sub-networks: a temporal structure generator (Gtemp) and a bar generator (Gbar).
  - Data augmentation methods include merging sparse tracks and segmenting MIDI files into manageable lengths.
- **Objective Evaluation Metrics**:
  - **Intra-track Metrics**: Includes metrics like Empty Bars (EB), Used Pitch Classes (UPC), Qualified Notes (QN), and Drum Patterns (DP).
  - **Inter-track Metric**: Tonal Distance (TD) measures harmonic relations between tracks.
- **User Study**: A listening test with 144 subjects indicated that the Hybrid model performed well in terms of musical structure and inter-track harmony.
- **Key Findings**:
  - MuseGAN can generate coherent, multi-track music segments with clear rhythmic patterns and harmonic relations.
  - The Composer and Hybrid models demonstrated superior cross-track harmony compared to the Jamming model.
- **Applications**: Can be used for generating multi-track symbolic music and extending to other domains involving sequential multi-track data.

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

### Music Transformer
- **Overview**: A transformer model specialized for generating symbolic music that maintains long-term coherence and structure by leveraging self-attention.
- **Relative Position Encoding**:
  - Integrates relative timing information, allowing the model to focus on relational distances rather than absolute positions, crucial for modeling long sequences of music.
  - Improves memory efficiency, reducing the space complexity from \(O(L^2D)\) to \(O(LD)\).
  - This enables the model to generate longer sequences (~2000 tokens) than previous attempts (~500 tokens).
- **Data Representation**:
  - **JSB Chorales**: Uses a serialized grid-like representation of polyphonic choral music. Timing is discretized to sixteenth notes, with relative attention capturing relational timing and pitch intervals.
  - **Piano-e-Competition**: MIDI-like event-based encoding with expressive timing and velocity, employing 128 NOTE_ON, 128 NOTE_OFF, 100 TIME_SHIFT, and 32 VELOCITY tokens. 
- **Experiments**:
  - Demonstrated improvement in perplexity and perceived coherence in generating piano performances, outperforming LSTM-based models like PerformanceRNN.
  - Priming experiments show that relative attention helps retain motifs and structural repetitions across longer sequences.
  - In a sequence-to-sequence task, the model was capable of generating accompaniments conditioned on given melodies.
- **Training Details**:
  - Used relative global and local attention to handle longer sequences, comparing multiple architectures and relative attention types.
  - Data augmentation with pitch transpositions and time-stretching, helping to generalize the model.
- **Human Evaluations**: Conducted listening tests that confirmed the relative Transformer as more coherent and musically structured compared to baseline Transformer models.

### Anticipatory Music Transformer
- Based on transformer architecture
- Generating structured symbolic music
- Uses anticipation mechanism to predict and align future musical content with past sequences, focusing on coherence and long-term dependencies.
  - Incorporates Anticipation Loss to encourage the model to align future sequences with past context, improving the planning of long-term structures.
  - Introduces a “lookahead” feature in the self-attention mechanism to enhance the generation of coherent musical sequences.
  - Models relationships between distant musical events, leading to improved structural consistency and stylistic coherence in generated music.
- Temporal representation of musical events:
  - Views music generation as a temporal point process where events (e.g., notes or chords) occur at specific time intervals. Each event is treated as a point in time, reflecting its timing and attributes like pitch, duration, and velocity.
  - Time-interval encoding: Encodes time intervals between successive events instead of using absolute time stamps, aligning with how humans perceive music rhythmically.
- Trained on Lakh MIDI dataset
