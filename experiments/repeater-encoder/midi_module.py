import mido
import utils
import math
import os
import numpy as np

# define some midi constants
MIDI_CHANNELS_NUMBER = 16
MIDI_NOTES_NUMBER = 128
MIDI_INSTRUMENTS_NUMBER = 128
INITIAL_VOLUME = 0
TEMPO = 500000
TIME_SIGNATURE = (4, 4)
QUANTIZATION = 32
# GRID_SIZE = QUANTIZATION * 2
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
                EPS = 0.01
                note_time = current_time - notes_start_times[programs[msg.channel]][msg.note]
                microseconds_per_denominator = TEMPO * (4 / TIME_SIGNATURE[1])
                microseconds_per_bar = microseconds_per_denominator * TIME_SIGNATURE[0]
                seconds_per_bar = microseconds_per_bar / 1000000
                if (note_time == 0):
                    continue
                note_length = utils.find_nearest(NOTE_LENGTHS, seconds_per_bar / note_time)
                bar =  notes_start_times[programs[msg.channel]][msg.note] / seconds_per_bar
                if abs(bar - math.ceil(bar)) < EPS:
                    bar = math.ceil(bar)
                else:
                    bar = math.floor(bar)
                note = {
                    'length': note_length,
                    'note': msg.note,
                    'volume': msg.velocity,
                    'onset_time': {
                        'bar': bar,
                        #hotfix for float % and division errors
                        'cell': round(round(round((int(round(notes_start_times[programs[msg.channel]][msg.note],3)*1000) % int(round(seconds_per_bar,3)*1000)), 3) / (seconds_per_bar / QUANTIZATION))/1000)
                    }
                }
                if (note['onset_time']['cell'] == QUANTIZATION):
                    note['onset_time']['cell'] = 0
                if (log_to_file):
                    print(note, file=f)
                notes[programs[msg.channel]].append(note.copy())
    return notes

def read_directories(dirs):
    result = []
    for dir in dirs:
        for root, subdirs, files in os.walk(dir):
            for file in files:
                path = root + "\\" + file
                if (path.endswith('.mid') or path.endswith('.midi')):
                    result.append(read_midi_file(path))
    non_empty_instruments = [False for _ in range(MIDI_INSTRUMENTS_NUMBER)]
    for i in range(MIDI_INSTRUMENTS_NUMBER):
        for song in result:
            if song[i] != []:
                non_empty_instruments[i] = True
    for i in range(len(result)):
        result[i] = [x for index, x in enumerate(result[i]) if non_empty_instruments[index] == True]
    return result

def notes_to_3d_piano_rolls(songs):
    SONG_LENGTH = 32 #song length in bars
    result = [[np.zeros(shape=(QUANTIZATION, MIDI_NOTES_NUMBER, len(songs[0]))) for _ in range(SONG_LENGTH)] for __ in range(len(songs))]
    for song_idx,song in enumerate(songs):
        for track_idx,track in enumerate(song):
            for note_idx,note in enumerate(track):
                if (note['onset_time']['bar'] < SONG_LENGTH):
                    for i in range(round(QUANTIZATION / note['length'])):
                        result[song_idx][note['onset_time']['bar']][note['onset_time']['cell'] + i][note['note']][track_idx] = note['volume']
    return result

def piano_roll_3d_to_midi(song):
    output = mido.MidiFile()
    track = mido.MidiTrack()

    for bar in song:
        for cell in bar:
            for note_volumes in cell:
                print(note_volumes[0],end = ' ')
            print("")

    for bar_index, bar in enumerate(song):
        note_lengths = [[0 for __ in range(len(bar[0][0]))] for _ in range(MIDI_NOTES_NUMBER)]
        playing_notes = [set() for __ in range(len(bar[0][0]))]
        for cell_index, cell in enumerate(bar):
            for note_height_index, note_volumes in enumerate(cell):
                for track_index, note_volume in enumerate(note_volumes):
                    if ((note_volume == 0 or cell_index == QUANTIZATION - 1) and cell_index > 0 and bar[cell_index - 1][note_height_index][track_index] > 0):
                        microseconds_per_denominator = TEMPO * (4 / TIME_SIGNATURE[1])
                        microseconds_per_bar = microseconds_per_denominator * TIME_SIGNATURE[0]
                        seconds_per_bar = microseconds_per_bar / 1000000
                        ticks_per_bar = mido.second2tick(seconds_per_bar, output.ticks_per_beat, TEMPO)
                        track.append(mido.Message('note_off', channel=track_index, note=note_height_index, velocity=int(note_volume), time=int(round(ticks_per_bar / QUANTIZATION * note_lengths[note_height_index][track_index]))))
                        note_lengths[note_height_index][track_index] = 0
            for note_height_index, note_volumes in enumerate(cell):
                for track_index, note_volume in enumerate(note_volumes):
                    if (note_volume > 0):
                        note_lengths[note_height_index][track_index] += 1
                    if (note_volume > 0 and (cell_index == 0 or bar[cell_index-1][note_height_index][track_index] == 0)): #if note start
                        track.append(mido.Message('note_on', channel=track_index, note=note_height_index, velocity=int(note_volume), time=0))
    output.tracks.append(track)
    return output


songs = notes_to_3d_piano_rolls(read_directories(["Music"]))
mid = piano_roll_3d_to_midi(songs[0])
mid.save('new_song.mid')
# notes_to_3d_piano_rolls(read_midi_file('aerozepp.mid', log_to_file=True))