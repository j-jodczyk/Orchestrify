import os
import shutil
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from music21 import converter
from music21.midi import MidiFile
import mido
import pretty_midi

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("filter_midi")


class ParseTimeoutError(Exception):
    """Exception raised when MIDI parsing exceeds the allowed timeout."""

    pass


def parse_with_timeout(file_path, timeout=20):
    """
    Parses a MIDI file within a specified timeout.

    Args:
        file_path (str): Path to the MIDI file to parse.
        timeout (int, optional): Maximum allowed parsing time in seconds. Defaults to 20.

    Returns:
        music21.stream.Score: Parsed MIDI file.

    Raises:
        ParseTimeoutError: If parsing exceeds the specified timeout.
        Exception: If an error occurs during parsing.
    """
    result = [None]
    exception = [None]

    def parse_file():
        try:
            result[0] = converter.parse(file_path)
        except Exception as e:
            exception[0] = e

    parse_thread = threading.Thread(target=parse_file, daemon=True)
    parse_thread.start()
    parse_thread.join(timeout)

    if parse_thread.is_alive():
        logger.warning(f"Timeout while parsing MIDI file: {file_path}")
        raise ParseTimeoutError(f"Timeout while parsing MIDI file: {file_path}")

    if exception[0] is not None:
        raise exception[0]

    return result[0]


def is_valid_midi_music21(file_path):
    """
    Checks if a MIDI file is valid.

    Args:
        file_path (str): Path to the MIDI file to validate.

    Returns:
        bool: True if the file is a valid MIDI, False otherwise.
    """
    try:
        mf = MidiFile()
        mf.open(file_path)
        mf.read()
        mf.close()
        return True
    except Exception as e:
        logger.warning(f"Invalid MIDI file: {file_path}. Error: {e}")
        return False


def is_valid_midi_mido(file_path):
    """
    Validates the structure of a MIDI file using mido.

    Args:
        file_path (str): Path to the MIDI file.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    try:
        mido.MidiFile(file_path)
        return True  # File is valid
    except Exception as e:
        logger.warning(f"Invalid MIDI file: {file_path}. Error: {e}")
        return False


def find_midi_files(directories):
    """
    Recursively searches directories for MIDI files.

    Args:
        directories (list of str): List of directory paths to search.

    Returns:
        list of str: List of paths to found MIDI files.
    """
    midi_files = []
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".mid"):
                    midi_files.append(os.path.join(root, file))
    return midi_files


def extract_midi_segment(midi_file, segment_duration=20):
    if segment_duration <= 0:
        raise ValueError("segment_duration must be greater than 0.")

    midi = pretty_midi.PrettyMIDI(midi_file)
    total_duration = midi.get_end_time()
    middle_time = total_duration / 2
    segment_start = max(0, middle_time - segment_duration / 2)
    segment_end = segment_start + segment_duration

    extracted_midi = pretty_midi.PrettyMIDI()

    for instrument in midi.instruments:
        new_instrument = pretty_midi.Instrument(program=instrument.program, is_drum=instrument.is_drum)
        for note in instrument.notes:
            if segment_start <= note.start <= segment_end:
                new_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=max(0, note.start - segment_start),
                    end=max(0, note.end - segment_start),
                )
                new_instrument.notes.append(new_note)
        extracted_midi.instruments.append(new_instrument)

    return extracted_midi


def process_midi_file(midi_file, output_directory, copy_only=True, segment_duration=20):
    """
    Processes a MIDI file, validates and parses it, and either copies it to the output directory or extracts a segment.

    Args:
        midi_file (str): Path to the MIDI file to process.
        output_directory (str): Directory to copy or save processed MIDI files.
        copy_only (bool, optional): If True, copies the file. If False, extracts the middle segment. Defaults to True.

    Returns:
        str or None: Path to the processed file if successful, otherwise None.
    """
    if not is_valid_midi_music21(midi_file):
        logger.warning(f"Skipping invalid MIDI file (music21 check): {midi_file}")
        return None

    if not is_valid_midi_mido(midi_file):
        logger.warning(f"Skipping invalid MIDI file (mido check): {midi_file}")
        return None

    try:
        _ = parse_with_timeout(midi_file, timeout=20)
        output_path = os.path.join(output_directory, os.path.basename(midi_file))

        if copy_only:
            logger.info(f"Copying full MIDI file: {midi_file}")
            shutil.copyfile(midi_file, output_path)
        else:
            logger.info(f"Extracting {segment_duration}s segment from MIDI file: {midi_file}")
            extracted_midi = extract_midi_segment(midi_file, segment_duration)
            extracted_midi.write(output_path)

        logger.info(f"Processed file: {midi_file} to {output_path}")
        return output_path
    except ParseTimeoutError:
        logger.warning(f"Skipping file due to timeout: {midi_file}")
    except Exception as e:
        logger.warning(f"Failed to parse MIDI file: {midi_file}. Reason: {e}")

    return None


def filter_and_collect_midi(midi_files, output_directory, max_workers=8, copy_only=True, segment_duration=20):
    """
    Filters and processes a list of MIDI files, copying or extracting valid ones to the output directory.

    Args:
        midi_files (list of str): List of MIDI file paths to process.
        output_directory (str): Directory to store processed MIDI files.
        max_workers (int, optional): Number of threads to use for concurrent processing. Defaults to 4.
        copy_only (bool, optional): If True, copies the files. If False, extracts middle segments. Defaults to True.

    Returns:
        list of str: List of paths to successfully processed MIDI files.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    logger.info(f"Found {len(midi_files)} MIDI files in the selected chunk.")

    processed_files = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_midi_file, f, output_directory, copy_only, segment_duration) for f in midi_files
        ]
        for future in futures:
            try:
                result = future.result()
                if result is not None:
                    processed_files.append(result)
            except Exception as e:
                logger.error(f"Error during MIDI file processing: {e}")

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

    copy_only_mode = input("Copy only (y/n)? ").strip().lower() == "y"

    filter_and_collect_midi(
        files_for_this_run, output_directory, max_workers=8, copy_only=copy_only_mode, segment_duration=20
    )
