import mido
from pathlib import Path
import logging
from note import Note
from constants import *
from logger import Logger

FILE_PATH = Path('song.mid')
log = Logger("midi_converter", logging.DEBUG)


def midi_to_notes(file_path: Path) -> [Note]:
    """Convert midi to array of notes"""
    notes = []
    active_notes = [[None for _ in range(MIDI_NOTES_NUMBER)] for _ in range(MIDI_INSTRUMENTS_NUMBER)]
    programs = [0 for _ in range(MIDI_CHANNELS_NUMBER)]
    current_time: float = 0

    for msg in mido.MidiFile(file_path):
        log.debug(msg)
        current_time += msg.time

        if msg.is_meta:
            continue  # todo

        if msg.type == 'program_change':
            programs[msg.channel] = msg.program

        if msg.type == 'note_on' and msg.velocity != 0:
            instrument = programs[msg.channel]
            active_notes[instrument][msg.note] = Note(instrument, current_time)

        if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            instrument = programs[msg.channel]
            note = active_notes[instrument][msg.note]
            assert note is not None
            note.end_time = current_time
            notes.append(note)
            active_notes[instrument][msg.note] = None


def midi_to_song(file_path: Path):
    notes = midi_to_notes(file_path)
    # notes[0].
    # # result array
    # # TODO: document structure
    # song = []
    # # time passed from last note_on/note_off event
    # current_time = 0
    #
    # for msg in mido.MidiFile(file_path):
    #     log.debug(msg)
    #     current_time += msg.time


def main():
    song = midi_to_song(FILE_PATH)
    print('end')


if __name__ == '__main__':
    main()
