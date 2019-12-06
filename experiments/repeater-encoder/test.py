from mido import MidiFile
import numpy as np

notes = []
midi = MidiFile("new_song.mid")
for msg in midi:
    print(msg)
