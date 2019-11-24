import mido
import utils
import math

def read_midi_file(filename):
    # define some midi constants
    CONTROL_VOLUME = 7
    MIDI_CHANNELS_NUMBER = 16
    MIDI_NOTES_NUMBER = 128
    INITIAL_VOLUME = 0
    TEMPO = 500000
    TIME_SIGNATURE = (4, 4)
    QUANTIZATION = 32
    GRID_SIZE = QUANTIZATION * 2
    NOTE_LENGTHS = utils.create_note_lengths(quantization = QUANTIZATION, use_dots = True)

    mid = mido.MidiFile(filename)
    notes = [[] for _ in range( MIDI_CHANNELS_NUMBER)]
    volumes_by_channels = [INITIAL_VOLUME for _ in range(MIDI_CHANNELS_NUMBER)]
    # times_by_channels = [0] * MIDI_CHANNELS_NUMBER
    current_time = 0
    notes_start_times = [[None for _ in range(MIDI_NOTES_NUMBER)] for _ in range(MIDI_CHANNELS_NUMBER)]
    f = open("log.txt", "w+")
    for msg in mid:
        note_length = 0
        if msg.is_meta:
            print(msg, file=f)
            if (msg.type == 'set_tempo'):
                TEMPO = msg.tempo
            if (msg.type == 'time_signature'):
                TIME_SIGNATURE = (msg.numerator, msg.denominator)
        else:
            print(msg, file=f)
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
                seconds_per_bar = microseconds_per_bar / 1000000
                note_length = utils.find_nearest(NOTE_LENGTHS, seconds_per_bar / note_time)
                print(note_length)
                print(notes_start_times[msg.channel][msg.note], file=f)
                print(current_time, file=f)
                print(seconds_per_bar, file=f)
                print((notes_start_times[msg.channel][msg.note] % seconds_per_bar), file=f)
                print(seconds_per_bar / GRID_SIZE, file=f)
                note = {
                    'length': note_length,
                    'note': msg.note,
                    'volume': msg.velocity,
                    'onset_time': {
                        'bar': math.floor(notes_start_times[msg.channel][msg.note] / seconds_per_bar),
                        'cell': round((notes_start_times[msg.channel][msg.note] % seconds_per_bar) / (seconds_per_bar / GRID_SIZE))
                    }
                }
                print(note, file=f)
                notes[msg.channel].append(note.copy())
    print('------------------')
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