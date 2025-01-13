# Orchestrify
WIMU-25Z project for generating musical accompaniment to single instrument MIDI track

## Project authors
- Erwin Balcerzak
- Miłosz Onyszczuk
- Julia Jodczyk

## Setup instructions:
[click here](./docs/SetUp.md)

## Design proposal:
[click here](./docs/DesignProposal.md)

## Clean Lakh DB:
https://huggingface.co/datasets/Milos121/cleaner_lakh_MMM

## Models
You can find trained models here:
- [Lakh](https://huggingface.co/rasta3050/aiguru_lakh)
- [Pure Pop](https://huggingface.co/rasta3050/aiguru_pop)
- [Pure Rock](https://huggingface.co/rasta3050/aiguru_rock)
- [Pure Jazz](https://huggingface.co/rasta3050/aiguru_jazz)
- [Pure Game Themes](https://huggingface.co/rasta3050/aiguru_game_themes)
- [TL Pop](https://huggingface.co/rasta3050/lakh_pop_transfer_model)
- [TL Rock](https://huggingface.co/rasta3050/lakh_rock_transfer_model)
- [TL Jazz](https://huggingface.co/rasta3050/lakh_jazz_transfer_model)
- [TL Game Themes](https://huggingface.co/rasta3050/lakh_game_themes_transfer_model)

# FMD
Here is FMD comparison of the models using [frehed-music-distance](https://github.com/jryban/frechet-music-distance).

| Genre            | Lakh   | Pure genre     | Transfer learning |
| ---------------- | ------ | -------------- | ---------------- |
| Pop              | 118.25 | 106.58         |  159.78          |
| Rock             | 115.66 | 117.28         |  170.48          |
| Game Themes      | 119.44 | 156.19         |  230.96          |
| Jazz             | 119.21 | 129.53         |  146.01          |
