
# Data retrieval:
Scraping midi data from `https://www.midiworld.com` website.

:::src.data.scrap_dataset_midiworld

# Data processing:

Some files in processed dataset had too long names for handling on Windows OS. To handle that, one of the preprocessing steps is to shorten their names.
:::src.data.shorten_paths

Some files were nested in subfolders and some where corrupted. During preprocessing we check if the files are valid, and move them to single folder. We accelerate preprocessing by splitting the data into chunks and running the script on multiple threads.

:::src.data.filter_dataset_chunks


# Other scripts:

## Creating sanity dataset
Script for creating sanity dataset containing simple melodies such as scales, arpeggio, Twinkle twinkle little star.

:::src.data.make_sanity_dataset
