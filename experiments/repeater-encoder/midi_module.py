import mido
import utils
import math
import numpy as np

# define some midi constants
MIDI_CHANNELS_NUMBER = 16
MIDI_NOTES_NUMBER = 128
MIDI_INSTRUMENTS_NUMBER = 128
INITIAL_VOLUME = 0
TEMPO = 500000
TIME_SIGNATURE = (4, 4)
QUANTIZATION = 32
GRID_SIZE = QUANTIZATION * 2
NOTE_LENGTHS = utils.create_note_lengths(quantization=QUANTIZATION, use_dots=True)

def read_midi_file(filename, log_to_file = False):
    # This function can only read files with constant tempo and time signature

    mid = mido.MidiFile(filename)
    notes = [[] for _ in range( MIDI_INSTRUMENTS_NUMBER)]
    current_time = 0
    notes_start_times = [[None for _ in range(MIDI_NOTES_NUMBER)] for _ in range(MIDI_INSTRUMENTS_NUMBER)]
    programs = [0 for _ in range( MIDI_CHANNELS_NUMBER)]

    if (log_to_file):
        f = open("log.txt", "w+")
        print('PARSING FILE:', filename, file=f)
        print('====================', file=f)
    for msg in mid:
        if (log_to_file):
            print(msg, file=f)
        if (msg.time != 0):
            current_time += msg.time
        if msg.is_meta:
            if (msg.type == 'set_tempo' and current_time == 0):
                TEMPO = msg.tempo
            if (msg.type == 'time_signature' and current_time == 0):
                TIME_SIGNATURE = (msg.numerator, msg.denominator)
            if (msg.type == 'set_tempo' and current_time != 0):
                print(filename, "- WARNING: Tempo change. This parser cannot handle multiple tempo files.")
            if (msg.type == 'time_signature' and current_time != 0):
                print(filename, "- WARNING: Time signature change. This parser cannot handle multiple time signature files.")
        else:
            if (msg.type == 'program_change' and current_time == 0):
                programs[msg.channel] = msg.program
            if (msg.type == 'note_on' and msg.velocity != 0):
                notes_start_times[programs[msg.channel]][msg.note] = current_time
            if (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                note_time = current_time - notes_start_times[programs[msg.channel]][msg.note]
                microseconds_per_denominator = TEMPO * (4 / TIME_SIGNATURE[1])
                microseconds_per_bar = microseconds_per_denominator * TIME_SIGNATURE[0]
                seconds_per_bar = microseconds_per_bar / 1000000
                note_length = utils.find_nearest(NOTE_LENGTHS, seconds_per_bar / note_time)
                note = {
                    'length': note_length,
                    'note': msg.note,
                    'volume': msg.velocity,
                    'onset_time': {
                        'bar': math.floor(notes_start_times[programs[msg.channel]][msg.note] / seconds_per_bar),
                        'cell': round((notes_start_times[programs[msg.channel]][msg.note] % seconds_per_bar) / (seconds_per_bar / GRID_SIZE))
                    }
                }
                if (log_to_file):
                    print(note, file=f)
                notes[programs[msg.channel]].append(note.copy())
    return (notes, programs)

read_midi_file('aerozepp.mid', log_to_file=True)