# import mido
#
# def read_midi_file(filename):
#     # define some midi constants
#     CONTROL_VOLUME = 7
#     MIDI_CHANNELS_NUMBER = 15
#     INITIAL_VOLUME = 0
#     TEMPO = 500000
#
#     mid = mido.MidiFile(filename)
#     notes = [[]] * MIDI_CHANNELS_NUMBER
#     volumes_by_channels = [INITIAL_VOLUME] * MIDI_CHANNELS_NUMBER
#     times_by_channels = [0] * MIDI_CHANNELS_NUMBER
#     for msg in mid:
#         if msg.is_meta:
#             print(msg)
#             if (msg.type == 'set_tempo'):
#                 TEMPO = msg.tempo
#         else:
#             print(msg)
#             if (msg.type == 'control_change'):
#                 if (msg.control==CONTROL_VOLUME):
#                     volumes_by_channels[msg.channel] = msg.value
#             if (msg.type == 'note_on'):
#                 # if (msg.velocity==0):
#                 #     treat like a note off
#                 notes[msg.channel].append(msg.note)
#             print (msg.time / (TEMPO / 1000000))
#     print('------------------')
#     print(mid.ticks_per_beat)
#     print(volumes_by_channels)
#     print(notes)
#
# read_midi_file('aerozepp_gp.mid')

import numpy as np
import pypianoroll
from matplotlib import pyplot as plt
import os

# dirs = ["Music"]
#
# for dir in dirs:
#     for root, subdirs, files in os.walk(dir):
#         for file in files:
#             path = root + "\\" + file
#             if not (path.endswith('.mid') or path.endswith('.midi')):
#                 continue
#             t = pypianoroll.Multitrack(path)
#             pypianoroll.save(path+'.npz', t)

t = pypianoroll.Multitrack('simplemidi2short.mid')
pypianoroll.save('saved.npz', t)