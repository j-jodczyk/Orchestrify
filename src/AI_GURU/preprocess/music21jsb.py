# Copyright 2021 Tristan Behrens.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3

import music21
from music21 import converter
from .. import logging
from music21.midi import MidiFile
from .preprocessutilities import events_to_events_data
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.create_logger("music21jsb")


class ParseTimeoutError(Exception):
    """Exception raised when MIDI parsing exceeds the allowed timeout."""
    pass


def parse_with_timeout(file_path):
    """
    Parses a MIDI file with a timeout to prevent hanging.

    Args:
        file_path (str): Path to the MIDI file.

    Returns:
        music21.stream.Score: Parsed music21 score.

    Raises:
        Exception: If parsing fails.
    """
    result = [None]
    exception = [None]

    def parse_file():
        try:
            result[0] = converter.parse(file_path)
        except Exception as e:
            exception[0] = e

    parse_thread = threading.Thread(target=parse_file)
    parse_thread.start()
    parse_thread.join()

    if exception[0] is not None:
        raise exception[0]

    return result[0]


def is_valid_midi(file_path):
    """
    Validates a MIDI file by checking its type and attempting to read it.

    Args:
        file_path (str): Path to the MIDI file.

    Returns:
        bool: True if the file is a valid MIDI file of type 0 or 1, False otherwise.
    """
    try:
        mf = MidiFile()
        mf.open(file_path)
        mf.read()
        mf.close()

        midi_type = mf.format
        if midi_type == 2:
            logger.warning(f"Unsupported MIDI file type: {file_path} is type 2.")
            return False

        return True
    except Exception as e:
        logger.warning(f"Invalid MIDI file: {file_path}. Reason: {e}")
        return False


def preprocess_music21(midi_files):
    """
    Preprocesses a list of MIDI files into training and validation datasets.

    Args:
        midi_files (list): List of file paths to MIDI files.

    Returns:
        tuple: (training data, validation data, flag indicating if no valid files were found).
    """
    valid_midi_files = [file for file in midi_files if is_valid_midi(file)]

    if not valid_midi_files:
        return [], [], True

    logger.info(f"Processing {len(valid_midi_files)} MIDI files.")

    with ThreadPoolExecutor(max_workers=8) as executor:
        songs = list(executor.map(parse_midi_file, valid_midi_files))

    songs = [song for song in songs if song is not None]

    split_index = int(0.8 * len(songs))
    songs_train = songs[:split_index]
    songs_valid = songs[split_index:]

    songs_data_train = preprocess_music21_songs(songs_train)
    songs_data_valid = preprocess_music21_songs(songs_valid)

    return songs_data_train, songs_data_valid, False


def parse_midi_file(midi_file):
    """
    Parses a MIDI file into a music21 stream.Score.

    Args:
        midi_file (str): Path to the MIDI file.

    Returns:
        music21.stream.Score: Parsed music21 score, or None if parsing fails.
    """
    try:
        return parse_with_timeout(midi_file)
    except ParseTimeoutError as e:
        logger.warning(str(e))
    except Exception as e:
        logger.warning(f"Failed to parse MIDI file: {midi_file}. Reason: {e}")
    return None


def preprocess_music21_songs(songs):
    """
    Preprocesses a list of music21 scores into tokenized data.

    Args:
        songs (list): List of music21.stream.Score objects.

    Returns:
        list: List of tokenized song data.
    """
    songs_data = []
    for song in songs:
        song_data = preprocess_music21_song(song)
        if song_data is not None:
            songs_data.append(song_data)

    return songs_data


def preprocess_music21_song(song):
    """
    Preprocesses a single music21 score into tokenized data.

    Args:
        song (music21.stream.Score): A music21 score object.

    Returns:
        dict: Tokenized song data, or None if the song is invalid.
    """
    meters = [meter.ratioString for meter in song.recurse().getElementsByClass(music21.meter.TimeSignature)]
    meters = list(set(meters))
    if len(meters) != 1:
        logger.debug(f"Skipping because of multiple measures.")
        return None
    elif meters[0] != "4/4":
        logger.debug(f"Skipping because of meter {meters[0]}.")
        return None

    song_data = {
        "title": song.metadata.title,
        "number": song.metadata.number,
        "tracks": [preprocess_music21_part(part, part_index) for part_index, part in enumerate(song.parts)],
    }

    return song_data


def preprocess_music21_part(part, part_index):
    """
    Preprocesses a music21 part into tokenized track data.

    Args:
        part (music21.stream.Part): A music21 part object.
        part_index (int): Index of the part in the song.

    Returns:
        dict: Tokenized track data.
    """
    track_data = {"name": part.partName, "number": part_index, "bars": []}

    for measure_index in range(1, 1000):  # music21 uses 1-based indexing for measures
        measure = part.measure(measure_index)
        if measure is None:
            break

        bar_data = preprocess_music21_measure(measure)
        if not bar_data["events"]:
            bar_data = {"events": [{"type": "TIME_DELTA", "delta": 4.0}]}

        track_data["bars"].append(bar_data)

    if not track_data["bars"]:
        logger.debug(f"Track '{part.partName or 'Unknown'}' has no valid bars.")
    return track_data


def preprocess_music21_measure(measure):
    """
    Preprocesses a music21 measure into tokenized bar data.

    Args:
        measure (music21.stream.Measure): A music21 measure object.

    Returns:
        dict: Tokenized bar data.
    """
    events = []
    for note in measure.recurse(classFilter=("Note")):
        events.append(("NOTE_ON", note.pitch.midi, 4 * note.offset))
        events.append(
            (
                "NOTE_OFF",
                note.pitch.midi,
                4 * note.offset + 4 * note.duration.quarterLength,
            )
        )

    bar_data = {"events": events_to_events_data(events)}
    return bar_data