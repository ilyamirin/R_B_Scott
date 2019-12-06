import pypianoroll
import os
import numpy as np
from argparse import Namespace
import pickle

QUANTIZATION = 32
MIDI_PROGRAMS_NUMBER = 128
MIDI_NOTES_NUMBER = 128
TIME_SIGNATURE = (4, 4)
MUSIC_DIR = "music"
DATASET_DIR = "dataset"

def read_midi_file(filename):
    #now can parse only midi type 0 files with constant tempo and (4,4) time signature
    # TODO: evaluate beat resolution based on time signature
    multitrack = pypianoroll.parse(filename, beat_resolution=round(QUANTIZATION/4))
    multitrack.pad_to_multiple(QUANTIZATION)
    multitrack.pad_to_same()
    return multitrack

def read_directory(dir):
    #read firectory
    #returns a dict with keys:
    #- songs: numpy array with shape (number of songs, song length in bars, song tracks, grid size, midi notes number)
    #- song_tracks_to_programs: maps dataset tracks to MIDI programs
    songs = []
    for root, subdirs, files in os.walk(dir):
        for file in files:
            path = os.path.join(root, file)
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
    #invert non_empty_programs so it maps midi channels into programs
    song_tracks_to_programs = {v: k for k, v in non_empty_programs.items()}
    return ({'songs': result,
             'song_tracks_to_programs': song_tracks_to_programs
             })

def write_song_to_midi(song, filename):
    #gets a 4-d array with shape (song length in bars, song tracks, grid size, midi notes number)
    tracks = [np.array([]) for _ in range(song.shape[1])]
    for bar_index, bar in enumerate(song):
        for track_index, track in enumerate(bar):
            if (tracks[track_index].size == 0):
                tracks[track_index] = track
            else:
                tracks[track_index] = np.concatenate((tracks[track_index], track))
    song_tracks_to_programs_file = open(os.path.join(DATASET_DIR, "song_tracks_to_programs.pkl"),"rb")
    song_tracks_to_programs =  pickle.load(song_tracks_to_programs_file)
    song_tracks_to_programs_file.close()
    for track_index, track in enumerate(tracks):
        tracks[track_index] = pypianoroll.Track(track, program=song_tracks_to_programs[track_index])
    multitrack = pypianoroll.Multitrack(tracks=tracks, beat_resolution=round(QUANTIZATION/4))
    multitrack.write(filename)

def create_dataset():
    dataset = read_directory(MUSIC_DIR)
    songs = dataset['songs']
    song_tracks_to_programs = dataset['song_tracks_to_programs']
    if not os.path.exists(DATASET_DIR):
        os.mkdir(DATASET_DIR)
    np.savez_compressed(os.path.join(DATASET_DIR, "songs"), songs)
    song_tracks_to_programs_file = open(os.path.join(DATASET_DIR, "song_tracks_to_programs.pkl"), "wb")
    pickle.dump(song_tracks_to_programs, song_tracks_to_programs_file)
    song_tracks_to_programs_file.close()

def load_dataset():
    #returns existing dataset that has been written by create_dataset function
    file =  np.load(os.path.join(DATASET_DIR, "songs.npz"))
    dataset = file.f.arr_0
    return dataset

pypianoroll_midi = Namespace(
    read_directory = read_directory,
    read_midi_file = read_midi_file,
    create_dataset = create_dataset,
    load_dataset = load_dataset,
)