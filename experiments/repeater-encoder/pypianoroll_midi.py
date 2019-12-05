import pypianoroll
import os
import numpy as np
from argparse import Namespace

QUANTIZATION = 32
MIDI_PROGRAMS_NUMBER = 128
MIDI_NOTES_NUMBER = 128
TIME_SIGNATURE = (4, 4)

def read_midi_file(filename):
    #now can parse only midi type 0 files with constant tempo and (4,4) time signature
    # TODO: evaluate beat resolution based on time signature
    return pypianoroll.parse(filename, beat_resolution=round(QUANTIZATION/4))

def read_directory(dir):
    #read firectory
    songs = []
    for root, subdirs, files in os.walk(dir):
        for file in files:
            path = root + "\\" + file
            if (path.endswith('.mid') or path.endswith('.midi')):
                songs.append(read_midi_file(path))

    #acknowledge non-empty programs and minimum song length
    non_empty_programs = {}
    non_empty_programs_count = 0
    max_song_length = 0
    for song in songs:
        for track in song.tracks:
            if not (track.program in non_empty_programs):
                # map existing programs into (0..num_existing_programs)
                non_empty_programs[track.program] = non_empty_programs_count
                non_empty_programs_count += 1
            max_song_length = max(max_song_length, round(track.pianoroll.shape[0] / QUANTIZATION))

    #create 3d piano roll from pypianoroll output
    result = np.zeros(shape=(len(songs), max_song_length, non_empty_programs_count, QUANTIZATION, MIDI_NOTES_NUMBER))
    for song_index, song in enumerate(songs):
        for track_index, track in enumerate(song.tracks):
            for bar_index, bar in enumerate(np.split(track.pianoroll, indices_or_sections=round(track.pianoroll.shape[0] / QUANTIZATION))):
                result[song_index][bar_index][track_index] = bar
    return result

pypianoroll_midi = Namespace(
    read_directory = read_directory,
    read_midi_file = read_midi_file,
)

read_directory("Music")