# import tensorflow as tf
from mido import MidiFile

# print(tf.test.is_gpu_available())
# exit()

midi = MidiFile("result.mid")
for msg in midi:
    print(msg)
#
# print("===============")
# midi = MidiFile("song.mid")
# for msg in midi:
#     print(msg)
