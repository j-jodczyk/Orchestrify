
# Data retrieval:
Scraping midi data from `https://www.midiworld.com` website.

:::src.data.scrap_dataset_midiworld

# Data processing:

Some files in processed dataset had too long names for handling on Windows OS. To handle that, one of the preprocessing steps is to shorten their names.
:::src.data.shorten_paths

Some files were nested in subfolders and some where corrupted. During preprocessing we check if the files are valid, and move them to single folder. We accelerate preprocessing by splitting the data into chunks and running the script on multiple threads.

:::src.data.filter_dataset_chunks


# Other scripts:
## Analyzing time delta impact
Due to the fact, that empty bars resulted in error in tokenization, we needed to come up with a workaround. The solution we came up with was adding `TIME_DELTA=4.0` events in such empty bars. To see how this impacts the sound of the processed midi files we created this script.

NOTE: music21 library on its own can change the sound a bit, due to the fact, that Control Change events are not processed correctly by it.

:::src.data.analyze_time_delta_impact

## Creating sanity dataset
Script for creating sanity dataset containing simple melodies such as scales, arpeggio, Twinkle twinkle little star.

:::src.data.make_sanity_dataset
