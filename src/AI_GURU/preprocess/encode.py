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

import itertools
import numpy as np
import random
import json


def encode_songs_data(songs_data, transpositions, permute, window_size_bars, hop_length_bars, density_bins, bar_fill):
    """
    Encodes songs into tokens without additional dataset context.

    Args:
        songs_data (list): List of dictionaries, each representing a single song.
        transpositions (list): List of transposition values.
        permute (bool): Whether to permute tracks randomly.
        window_size_bars (int): Number of bars in a window.
        hop_length_bars (int): Hop length between consecutive windows.
        density_bins (list): Density bins for note events.
        bar_fill (bool): Whether to include bar fills.

    Returns:
        list: List of token sequences representing all songs.
    """

    # This will be returned.
    token_sequences = []

    # Go through all songs.
    for song_data in songs_data:
        token_sequences += encode_song_data(
            song_data,
            transpositions,
            permute,
            window_size_bars,
            hop_length_bars,
            density_bins,
            bar_fill,
        )

    # Done.
    return token_sequences


def encode_song_data_singular(song_data, density):
    """
    Used to encode song data on per one midi file basis - as opposed to
    encode_song_data, which is used to encode a song that is a part of
    a greater dataset.

    Args:
        song_data (dict): Dictionary representing a single song.
        density (int): Density bin for the song.

    Returns:
        list: Token sequence for the song.

    NOTE: Doesn't give the option of bar fill, since our project is not focused on that
    """
    token_sequences = []

    token_sequences += ["PIECE_START"]
    if song_data is None:
        return token_sequences
    track_data_indices = list(range(len(song_data["tracks"])))

    for track_data_index in track_data_indices:
        track_data = song_data["tracks"][track_data_index]
        encoded_track_data = encode_track_data_singular(track_data, density)
        token_sequences += encoded_track_data

    return token_sequences


def encode_track_data_singular(track_data, density):
    """
    Used to encode trak data on per one midi file basis - as opposed to
    encode_trak_data, which is used to encode tracks from a song that is a part of
    a greater dataset.

    Args:
        track_data (dict): Dictionary representing track data.
        density (int): Density bin for the track.

    Returns:
        list: Token sequence for the track.
    """
    tokens = ["TRACK_START"]
    number = track_data["number"]

    if not track_data.get("drums", False):
        tokens += [f"INST={number}"]
    else:
        tokens += ["INST=DRUMS"]

    tokens += [f"DENSITY={density}"]
    for bar_data in track_data["bars"]:
        tokens += encode_bar_data_no_transposition(bar_data)

    tokens += ["TRACK_END"]
    return tokens


def encode_bar_data_no_transposition(bar_data):
    """
    Encodes bar data without transposition (because I don't understand it)

    Args:
        bar_data (dict): Dictionary representing bar data.

    Returns:
        list: Token sequence for the bar.

    NOTE: Doesn't give the option of bar fill, since our project is not focued on that
    """
    tokens = ["BAR_START"]
    for event_data in bar_data["events"]:
        tokens += [encode_event_data_no_transposition(event_data)]
    tokens += ["BAR_END"]
    return tokens


def encode_event_data_no_transposition(event_data):
    """
    Encodes event data without transposition

    Args:
        event_data (dict): Dictionary representing event data.

    Returns:
        str: Encoded event as a string.
    """
    return encode_event_data(event_data, 0)


def encode_song_data(song_data, transpositions, permute, window_size_bars, hop_length_bars, density_bins, bar_fill):
    """
    Encodes a single song into token sequences with dataset context.

    Args:
        song_data (dict): Dictionary representing a single song.
        transpositions (list): List of transposition values.
        permute (bool): Whether to permute tracks randomly.
        window_size_bars (int): Number of bars in a window.
        hop_length_bars (int): Hop length between consecutive windows.
        density_bins (list): Density bins for note events.
        bar_fill (bool): Whether to include bar fills.

    Returns:
        list: List of token sequences for the song.
    """

    # This will be returned.
    token_sequences = []

    # Count the bars.
    bars = get_bars_number(song_data)

    # For iterating over the bars.
    bar_indices = get_bar_indices(bars, window_size_bars, hop_length_bars)

    # Go through all combinations.
    count = 0
    for (bar_start_index, bar_end_index), transposition in itertools.product(bar_indices, transpositions):

        # Start empty
        token_sequence = []

        # Do bar fill if necessary.
        if bar_fill:
            track_data = random.choice(song_data["tracks"])
            bar_data = random.choice(track_data["bars"][bar_start_index:bar_end_index])
            bar_data_fill = {"events": bar_data["events"]}
            bar_data["events"] = "bar_fill"

        # Start with the tokens.
        token_sequence += ["PIECE_START"]

        # Get the indices. Permute if necessary.
        track_data_indices = list(range(len(song_data["tracks"])))
        if permute:
            random.shuffle(track_data_indices)

        # Encode the tracks.
        for track_data_index in track_data_indices:
            track_data = song_data["tracks"][track_data_index]

            # Encode the track. Insert density tokens. Also transpose.
            encoded_track_data = encode_track_data(
                track_data, density_bins, bar_start_index, bar_end_index, transposition
            )
            token_sequence += encoded_track_data

        # Encode the fill tokens.
        if bar_fill:
            token_sequence += encode_bar_data(bar_data_fill, transposition, bar_fill=True)

        token_sequences += [token_sequence]
        count += 1

    # Done
    return token_sequences


def encode_track_data(track_data, density_bins, bar_start_index, bar_end_index, transposition):
    """
    Encodes track data for a single track within dataset context.

    Args:
        track_data (dict): Dictionary representing track data.
        density_bins (list): Density bins for note events.
        bar_start_index (int): Starting bar index.
        bar_end_index (int): Ending bar index.
        transposition (int): Transposition value.

    Returns:
        list: Token sequence for the track.
    """

    tokens = []

    tokens += ["TRACK_START"]

    # Set instrument.
    number = track_data["number"]

    # Set the instrument if it is a harmonic one.
    if not track_data.get("drums", False):
        tokens += [f"INST={number}"]

    # Set the instrument if it is drums. Also do not transpose drums.
    else:
        tokens += ["INST=DRUMS"]
        transposition = 0

    # Count note on events.
    note_on_events = 0
    for bar_data in track_data["bars"][bar_start_index:bar_end_index]:
        if bar_data["events"] == "bar_fill":
            continue
        for event_data in bar_data["events"]:
            if event_data["type"] == "NOTE_ON":
                note_on_events += 1

    # Determine density.
    density = np.digitize(note_on_events, density_bins)
    tokens += [f"DENSITY={density}"]

    # Encode the bars.
    for bar_data in track_data["bars"][bar_start_index:bar_end_index]:
        tokens += encode_bar_data(bar_data, transposition)

    tokens += ["TRACK_END"]

    return tokens


def encode_bar_data(bar_data, transposition):
    tokens = []
    tokens += ["BAR_START"]

    for event_data in bar_data["events"]:
        tokens += [encode_event_data(event_data, transposition)]

    tokens += ["BAR_END"]

    return tokens


def encode_event_data(event_data, transposition):
    if event_data["type"] == "NOTE_ON":
        return event_data["type"] + "=" + str(event_data["pitch"] + transposition)
    elif event_data["type"] == "NOTE_OFF":
        return event_data["type"] + "=" + str(event_data["pitch"] + transposition)
    elif event_data["type"] == "TIME_DELTA":
        return event_data["type"] + "=" + str(event_data["delta"])


def get_density_bins(songs_data, window_size_bars, hop_length_bars, bins):
    """
    Computes density bins based on note-on event counts.

    Args:
        songs_data (list): List of dictionaries, each representing a song.
        window_size_bars (int): Number of bars in a window.
        hop_length_bars (int): Hop length between consecutive windows.
        bins (int): Number of density bins.

    Returns:
        list: List of density bin thresholds.
    """

    # Go through all songs and count the note on events for each window.\
    distribution = []
    for song_data in songs_data:
        # Count the bars.
        bars = get_bars_number(song_data)

        # Iterate over over the tracks and the bars.
        bar_indices = get_bar_indices(bars, window_size_bars, hop_length_bars)
        for track_data in song_data["tracks"]:
            for bar_start_index, bar_end_index in bar_indices:

                # Go through the bars and count notes.
                count = 0
                for bar in track_data["bars"][bar_start_index:bar_end_index]:
                    count += len([event for event in bar["events"] if event["type"] == "NOTE_ON"])

                # Do not count empty tracks.
                if count != 0:
                    distribution += [count]

    if len(distribution) == 0:
        raise ValueError("Density distribution is empty. Ensure training data contains valid songs.")

    # Compute the quantiles, which will become the density bins.
    quantiles = []
    for i in range(100 // bins, 100, 100 // bins):
        quantile = np.percentile(distribution, i)
        quantiles += [quantile]
    return quantiles


def get_density_bins_from_json_files(json_paths, window_size_bars, hop_length_bars, bins):
    """
    Computes density bins based on note-on event counts from JSON files.

    Args:
        json_paths (list): List of paths to JSON files.
        window_size_bars (int): Number of bars in a window.
        hop_length_bars (int): Hop length between consecutive windows.
        bins (int): Number of density bins.

    Returns:
        list: List of density bin thresholds.
    """

    # Go through all songs and count the note on events for each window.\
    distribution = []
    for json_path in json_paths:

        # Open the file and get the data.
        song_data = json.load(open(json_path, "r"))

        # Count the bars.
        bars = get_bars_number(song_data)

        # Iterate over over the tracks and the bars.
        bar_indices = get_bar_indices(bars, window_size_bars, hop_length_bars)
        for track_data in song_data["tracks"]:
            for bar_start_index, bar_end_index in bar_indices:

                # Go through the bars and count notes.
                count = 0
                for bar in track_data["bars"][bar_start_index:bar_end_index]:
                    count += len([event for event in bar["events"] if event["type"] == "NOTE_ON"])

                # Do not count empty tracks.
                if count != 0:
                    distribution += [count]

    # Compute the quantiles, which will become the density bins.
    quantiles = []
    for i in range(100 // bins, 100, 100 // bins):
        quantile = np.percentile(distribution, i)
        quantiles += [quantile]
    return quantiles


def get_bars_number(song_data):
    """
    Computes the maximum number of bars across all tracks in a song.

    Args:
        song_data (dict): Dictionary representing a song.

    Returns:
        int: Maximum number of bars.
    """
    bars = [len(track_data["bars"]) for track_data in song_data["tracks"]]
    bars = max(bars)
    return bars


def get_bar_indices(bars, window_size_bars, hop_length_bars):
    """
    Computes the start and end indices for sliding windows over bars.

    Args:
        bars (int): Total number of bars.
        window_size_bars (int): Number of bars in a window.
        hop_length_bars (int): Hop length between consecutive windows.

    Returns:
        list: List of tuples (start_index, end_index).
    """
    return list(
        zip(
            range(0, bars, hop_length_bars),
            range(window_size_bars, bars, hop_length_bars),
        )
    )
