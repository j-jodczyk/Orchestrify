## Literature Overview

| Title                                             | Year  | Article link                                                             | Source code link                   | Description                   |
|---------------------------------------------------|-------|--------------------------------------------------------------------------|------------------------------------|-------------------------------|
| SingSong                                          | 2023  | https://arxiv.org/abs/2301.12662                                         |                  |             |
| Counterpoint by convolution                       | 2019  | https://arxiv.org/pdf/1903.07227                                         |                  |             |
| Musegan                                           | 2018  | https://arxiv.org/abs/1709.06298                                         |                  |             |
| Literature survey of multi-track music generation | 2023  | https://doi.org/10.1007/s11227-022-04914-5                               |                  |             |
| MMM                                               | 2020  | https://arxiv.org/pdf/2008.06048                                         | https://github.com/AI-Guru/MMM-JSB<br>demo: https://jeffreyjohnens.github.io/MMM/ | [see below](#MMM) |
| LakhNES                                           | 2019  | https://arxiv.org/pdf/1907.04868                                         |                  |             |
| A transformer generative adversarial network...   |       | https://ietresearch.onlinelibrary.wiley.com/doi/epdf/10.1049/cit2.12065  |                  |             |
|  |   |   |   |   |


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
