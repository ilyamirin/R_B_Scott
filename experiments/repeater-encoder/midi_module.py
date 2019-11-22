import mido
import math
import numpy as np

def find_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return array[idx-1]
    else:
        return array[idx]

def read_midi_file(filename):
    # define some midi constants
    CONTROL_VOLUME = 7
    MIDI_CHANNELS_NUMBER = 15
    INITIAL_VOLUME = 0
    TEMPO = 500000
    TIME_SIGNATURE = (4, 4)
    QUANTIZATION = 16
    NOTE_LENGTHS = [1, 1.33, 2, 2.67, 4, 5.33, 8, 10.67, 16, 32]

    mid = mido.MidiFile(filename)
    notes = [[]] * MIDI_CHANNELS_NUMBER
    volumes_by_channels = [INITIAL_VOLUME] * MIDI_CHANNELS_NUMBER
    times_by_channels = [0] * MIDI_CHANNELS_NUMBER
    for msg in mid:
        if msg.is_meta:
            print(msg)
            if (msg.type == 'set_tempo'):
                TEMPO = msg.tempo
            if (msg.type == 'time_signature'):
                TIME_SIGNATURE = (msg.numerator, msg.denominator)
        else:
            print(msg)
            if (msg.type == 'control_change'):
                if (msg.control==CONTROL_VOLUME):
                    volumes_by_channels[msg.channel] = msg.value
            if (msg.type == 'note_on'):
                # if (msg.velocity==0):
                #     treat like a note off
                notes[msg.channel].append(msg.note)
            if (msg.time != 0):
                microseconds_per_denominator = TEMPO * (4 / TIME_SIGNATURE[1])
                microseconds_per_bar = microseconds_per_denominator * TIME_SIGNATURE[0]
                print (find_nearest(NOTE_LENGTHS, (microseconds_per_bar / 1000000) / msg.time))
    print('------------------')
    print(mid.ticks_per_beat)
    print(volumes_by_channels)
    print(notes)

read_midi_file('aerozepp.mid')

import numpy as np
import pypianoroll
from matplotlib import pyplot as plt
import os

# # dirs = ["Music"]
# #
# # for dir in dirs:
# #     for root, subdirs, files in os.walk(dir):
# #         for file in files:
# #             path = root + "\\" + file
# #             if not (path.endswith('.mid') or path.endswith('.midi')):
# #                 continue
# #             t = pypianoroll.Multitrack(path)
# #             pypianoroll.save(path+'.npz', t)
#
# t = pypianoroll.Multitrack('simplemidi2short.mid')
# pypianoroll.save('saved.npz', t)