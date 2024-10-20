## Design Proposal
### Planned experiments
The goal of this project is to create a model that will be capable of creating a multi-instrumental accopaniament given a track with one instrument in a form of a MIDI file. We want to explore the possibility of creating good sounding, multi-instrumental melodies with the help of ML.

As a starting point we will train our model with only one instrument type, for example guitar (the instrument will be chosen depending on the dataset). If there will be time, we plan on exploring the model's performance with different instruments as input.

The following will be explored:
- methods for generating multi-channel MIDI files from a single instrument track,
- model's performance with different instruments as input
- evaluation metrics for generated music

### Planned functionalities
The primary goal of our project is to create a multi-instrumental accompaniment based on a track featuring a single instrument.

For user-friendly interaction, we will create a dedicated GUI, which will allow users to upload MIDI tracks and later download the resulting MIDI files.


### Planned schedule

| Week   | Task  |
| ---    | ---   |
| 21.10 - 27.10 | Anaysis of literature |
| 28.10 - 03.11 | Dataset selection and preprocessing |
| 04.11 - 10.11 | Start implementing model |
| 11.11 - 17.11 | Model training |
| 18.11 - 24.11 | Evaluate first results |
| 24.11 - 01.12 | Model adjustments according to test results |
| 02.12 - 08.12 | Training and evaluation |
| 09.12 - 15.12 | Model tuning |
| 16.11 - 22.12 | UI |
| 23.12 - 29.12 | Christmass |
| 30.12 - 05.01 | Final tests |
| 06.01 - 12.01 | Documentation and final report |
| 13.01 - 19.01 | Submission deadline |


### Technological stack:
- Project structure
    - `black` linter
    - `venv` virtual environment
    - `make` for testing and running
- Model
    - `pretty-midi` for midi file manipulation
    - `PyTorch` as a machine learning library
    - `transformers` access to pre-trained transformers and useful functions
    - `MIDItok` for midi files tokanization
- GUI
    - `FastAPI` for backend
    - `React` for frontend

### Bibliography
- Donahue, C., Caillon, A., Roberts, A., Manilow, E., Esling, P., Agostinelli, A., Verzetti, M., Simon, I., Pietquin, O., Zeghidour, N., & Engel, J. (2023). SingSong: Generating musical accompaniments from singing. arXiv: https://arxiv.org/abs/2301.12662
- Huang, C.-Z. A., Cooijmans, T., Roberts, A., Courville, A., & Eck, D. (2019). Counterpoint by convolution. arXiv: https://arxiv.org/pdf/1903.07227
- Dong, H.-W., Hsiao, W.-Y., Yang, L.-C., & Yang, Y.-H. (2018). Musegan: Multi-track sequential generative adversarial networks for symbolic music generation and accompaniment. In *Proceedings of the AAAI Conference on Artificial Intelligence* (Vol. 32, No. 1). arXiv: https://arxiv.org/abs/1709.06298
- Liu, W. (2023). Literature survey of multi-track music generation model based on generative confrontation network in intelligent composition. J Supercomput 79, 6560–6582  https://doi.org/10.1007/s11227-022-04914-5


### Additional remarks:
#### Analysis of literature end result:
- Have a few datasets to choose from
- Have a model picked out (CNN, Transformer, ...)
- Have testing strategy picked out (except for our own opinion)
- Have tokanization method picked out
- Is there an existing model that we can leverage and fine-tune using transfer learning, or will we need to design and train our model from scratch?
- Collected findings in a document
    - addidionally: is source code available


#### Things that keep in mind for Dataset preprocessing:
- We'll divide each midi file into sequences of equal length. After this I would suggest filtering out the samples where majority of sequence is one instrument playing solo to push the model to create richer compositions.
