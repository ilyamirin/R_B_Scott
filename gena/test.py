import tensorflow as tf
from mido import MidiFile

midi = MidiFile("result.mid")
for msg in midi:
    print(msg)

