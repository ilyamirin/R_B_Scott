import math
from typing import List

import mido
from pathlib import Path
import logging

from mido.midifiles.midifiles import DEFAULT_TICKS_PER_BEAT, DEFAULT_TEMPO

from note import Note
from constants import *
from logger import Logger

FILE_PATH = Path('song.mid')
log = Logger("midi_converter", logging.DEBUG)


def append_note(programs: [], active_notes: [], notes: [], msg: mido.Message, current_time: float):
    instrument = programs[msg.channel]
    note = active_notes[instrument][msg.note]
    if note is None:
        return
    note.end_time = current_time
    notes.append(note)
    active_notes[instrument][msg.note] = None


def midi_to_notes(midi: mido.MidiFile) -> List[Note]:
    """Convert midi to array of notes"""
    notes: List[Note] = []
    active_notes = [[None for _ in range(MIDI_NOTES_NUMBER)] for _ in range(MIDI_INSTRUMENTS_NUMBER)]
    programs = [0 for _ in range(MIDI_CHANNELS_NUMBER)]
    current_time: float = 0

    for message_index, msg in enumerate(midi):
        log.debug("{}: {}".format(message_index, msg))
        current_time += msg.time

        if msg.is_meta:
            continue  # todo

        if msg.type == 'program_change':
            programs[msg.channel] = msg.program

        if msg.type == 'note_on' and msg.velocity != 0:
            instrument = programs[msg.channel]
            # if note changes velocity
            active_note = active_notes[instrument][msg.note]
            if active_note is not None:
                append_note(programs, active_notes, notes, msg, current_time)

            active_notes[instrument][msg.note] = Note(msg.note, instrument, msg.velocity, current_time)

        if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            append_note(programs, active_notes, notes, msg, current_time)

    return notes


def midi_to_song(file_path: Path) -> []:
    midi = mido.MidiFile(file_path)
    notes = midi_to_notes(midi)
    total_quants = math.ceil(midi.length * QUANTIZATION)
    roll = [[[0 for _ in range(MIDI_NOTES_NUMBER)] for _ in range(MIDI_INSTRUMENTS_NUMBER)] for _ in range(total_quants)]

    for note in notes:
        start_quant = math.ceil(note.start_time * QUANTIZATION)
        end_quant = math.floor(note.end_time * QUANTIZATION)
        for i in range(start_quant, end_quant + 1):
            roll[i][note.instrument][note.note] = note.velocity

    return roll


def song_to_midi(song: []):
    output = mido.MidiFile()
    track = mido.MidiTrack()

    # todo parse correct instruments
    prev_state = [[0 for _ in range(MIDI_NOTES_NUMBER)] for _ in range(MIDI_INSTRUMENTS_NUMBER)]
    time = 0
    for quant, instruments in enumerate(song):
        for instrument, notes in enumerate(instruments):
            for note, velocity in enumerate(notes):
                if prev_state[instrument][note] == 0 and velocity != 0:
                    track.append(mido.Message('note_on', channel=2, note=note, velocity=velocity,
                                              time=math.ceil(mido.second2tick(time, DEFAULT_TICKS_PER_BEAT,
                                                                              DEFAULT_TEMPO))))
                    time = 0
                if prev_state[instrument][note] != 0 and (velocity == 0 or quant == len(song)-1):
                    track.append(mido.Message('note_off', channel=2, note=note, velocity=0,
                                              time=math.ceil(mido.second2tick(time, DEFAULT_TICKS_PER_BEAT,
                                                                              DEFAULT_TEMPO))))
                    time = 0

        prev_state = instruments
        time += 1/QUANTIZATION

    output.tracks.append(track)
    output.save('1.mid')


def main():
    song = midi_to_song(FILE_PATH)
    song_to_midi(song)
    # f = open("log.txt", "w+")
    # f.write(str(song))
    print('end')


if __name__ == '__main__':
    main()
