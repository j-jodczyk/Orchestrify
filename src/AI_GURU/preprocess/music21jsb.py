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
from source import logging
from music21.midi import MidiFile
from source.preprocess.preprocessutilities import events_to_events_data
import os
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.create_logger("music21jsb")


class ParseTimeoutError(Exception):
    pass


def parse_with_timeout(file_path):
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
    try:
        mf = MidiFile()
        mf.open(file_path)
        mf.read()
        mf.close()
        return True
    except Exception as e:
        logger.warning(f"Invalid MIDI file: {file_path}. Reason: {e}")
        return False


def preprocess_music21(midi_files):
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

    songs_data_train = preprocess_music21_songs(songs_train, train=True)
    songs_data_valid = preprocess_music21_songs(songs_valid, train=False)

    return songs_data_train, songs_data_valid, False


def parse_midi_file(midi_file):
    try:
        return parse_with_timeout(midi_file)
    except ParseTimeoutError as e:
        logger.warning(str(e))
    except Exception as e:
        logger.warning(f"Failed to parse MIDI file: {midi_file}. Reason: {e}")
    return None


def preprocess_music21_songs(songs, train):
    songs_data = []
    for song in songs:
        song_data = preprocess_music21_song(song, train)
        if song_data is not None:
            songs_data.append(song_data)

    return songs_data


def preprocess_music21_song(song, train):
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
        "tracks": [preprocess_music21_part(part, part_index, train) for part_index, part in enumerate(song.parts)],
    }

    return song_data


def preprocess_music21_part(part, part_index, train):
    track_data = {"name": part.partName, "number": part_index, "bars": []}

    for measure_index in range(1, 1000):  # music21 uses 1-based indexing for measures
        measure = part.measure(measure_index)
        if measure is None:
            break

        bar_data = preprocess_music21_measure(measure, train)
        if not bar_data["events"]:
            bar_data = {"events": [{"type": "TIME_DELTA", "delta": 4.0}]}

        track_data["bars"].append(bar_data)

    if not track_data["bars"]:
        logger.debug(f"Track '{part.partName or 'Unknown'}' has no valid bars.")
    return track_data


def preprocess_music21_measure(measure, train):
    events = []
    for note in measure.recurse(classFilter=("Note")):
        events.append(("NOTE_ON", note.pitch.midi, 4 * note.offset))
        events.append(("NOTE_OFF", note.pitch.midi, 4 * note.offset + 4 * note.duration.quarterLength))

    bar_data = {"events": events_to_events_data(events)}
    return bar_data
