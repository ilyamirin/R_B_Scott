import mido
import utils

def read_midi_file(filename):
    # define some midi constants
    CONTROL_VOLUME = 7
    MIDI_CHANNELS_NUMBER = 16
    MIDI_NOTES_NUMBER = 128
    INITIAL_VOLUME = 0
    TEMPO = 500000
    TIME_SIGNATURE = (4, 4)
    NOTE_LENGTHS = utils.create_note_lengths(quantization = 32, use_dots = True)

    mid = mido.MidiFile(filename)
    notes = [[] for _ in range( MIDI_CHANNELS_NUMBER)]
    volumes_by_channels = [INITIAL_VOLUME for _ in range(MIDI_CHANNELS_NUMBER)]
    # times_by_channels = [0] * MIDI_CHANNELS_NUMBER
    current_time = 0
    notes_start_times = [[None for _ in range(MIDI_NOTES_NUMBER)] for _ in range(MIDI_CHANNELS_NUMBER)]
    for msg in mid:
        note_length = 0
        if msg.is_meta:
            print(msg)
            if (msg.type == 'set_tempo'):
                TEMPO = msg.tempo
            if (msg.type == 'time_signature'):
                TIME_SIGNATURE = (msg.numerator, msg.denominator)
        else:
            print(msg)
            if (msg.type == 'control_change'):
                if (msg.control == CONTROL_VOLUME):
                    volumes_by_channels[msg.channel] = msg.value
            if (msg.time != 0):
                current_time += msg.time
            if (msg.type == 'note_on'):
                # if (msg.velocity==0):
                #     treat like a note off
                notes_start_times[msg.channel][msg.note] = current_time
            if (msg.type == 'note_off'):
                note_time = current_time - notes_start_times[msg.channel][msg.note]
                microseconds_per_denominator = TEMPO * (4 / TIME_SIGNATURE[1])
                microseconds_per_bar = microseconds_per_denominator * TIME_SIGNATURE[0]
                note_length = utils.find_nearest(NOTE_LENGTHS, (microseconds_per_bar / 1000000) / note_time)
                print(note_length)
                note = {
                    'length': note_length,
                    'note': msg.note,
                    'volume': msg.velocity,
                    'noset_time': notes_start_times[msg.channel][msg.note]
                }
                notes[msg.channel].append(note.copy())
    print('------------------')
    print(mid.ticks_per_beat)
    print(volumes_by_channels)
    print(notes)

read_midi_file('simple_midi_2_tracks.mid')

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