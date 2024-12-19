import os
import shutil
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from music21 import converter
from music21.midi import MidiFile

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("filter_midi")


class ParseTimeoutError(Exception):
    pass


# Code for filtering MIDI files from a dataset based on their parsing time or other issues.
def parse_with_timeout(file_path, timeout=5):
    result = [None]
    exception = [None]

    def parse_file():
        try:
            result[0] = converter.parse(file_path)
        except Exception as e:
            exception[0] = e

    parse_thread = threading.Thread(target=parse_file)
    parse_thread.start()
    parse_thread.join(timeout)

    if parse_thread.is_alive():
        logger.warning(f"Timeout while parsing MIDI file: {file_path}")
        raise ParseTimeoutError(f"Timeout while parsing MIDI file: {file_path}")

    if exception[0] is not None:
        raise exception[0]

    return result[0]


def is_valid_midi(file_path):
    try:
        mf = MidiFile()
        mf.open(file_path)
        mf.read()
        mf.close()
        return True
    except Exception as e:
        logger.warning(f"Invalid MIDI file: {file_path}. Reason: {e}")
        return False


def find_midi_files(directories):
    midi_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".mid"):
                    midi_files.append(os.path.join(root, file))
    return midi_files


def process_midi_file(midi_file, output_directory):
    if not is_valid_midi(midi_file):
        return None

    try:
        _ = parse_with_timeout(midi_file, timeout=5)
        output_path = os.path.join(output_directory, os.path.basename(midi_file))
        shutil.copyfile(midi_file, output_path)
        logger.info(f"Copied valid file: {midi_file} to {output_path}")
        return output_path
    except ParseTimeoutError:
        logger.warning(f"Skipping file due to timeout: {midi_file}")
    except Exception as e:
        logger.warning(f"Failed to parse MIDI file: {midi_file}. Reason: {e}")

    return None


def filter_and_collect_midi(midi_files, output_directory, max_workers=4):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    logger.info(f"Found {len(midi_files)} MIDI files in the selected chunk.")

    processed_files = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_midi_file, f, output_directory) for f in midi_files]
        for future in futures:
            result = future.result()
            if result is not None:
                processed_files.append(result)

    logger.info(f"Done processing. {len(processed_files)} files successfully copied to {output_directory}.")
    return processed_files


if __name__ == "__main__":
    input_directories = [
        "path_to_dataset_we_want_to_filter",
    ]

    output_directory = "output_path"

    total_parts = 6

    all_midi_files = find_midi_files(input_directories)

    if not all_midi_files:
        logger.error("No MIDI files found in the specified directories.")
        exit(1)

    all_midi_files.sort()

    total_files = len(all_midi_files)
    logger.info(f"Total MIDI files found: {total_files}")

    part_to_run = int(input(f"Enter which part to run (1-{total_parts}): "))

    if not (1 <= part_to_run <= total_parts):
        logger.error(f"Invalid part number. Please choose between 1 and {total_parts}.")
        exit(1)

    chunk_size = (total_files + total_parts - 1) // total_parts
    start_index = (part_to_run - 1) * chunk_size
    end_index = min(start_index + chunk_size, total_files)

    files_for_this_run = all_midi_files[start_index:end_index]

    logger.info(f"Processing part {part_to_run}/{total_parts} with {len(files_for_this_run)} files.")

    filter_and_collect_midi(files_for_this_run, output_directory, max_workers=8)
