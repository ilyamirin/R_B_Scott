import math
import numpy as np
from argparse import Namespace

def find_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return array[idx-1]
    else:
        return array[idx]

NOTE_LENGTHS = {
    'WHOLE': 1,
    'HALF': 2,
    'QUATER': 4,
    'EIGHTH': 8,
    'SIXTEENTH': 16,
    'THIRTY-SECOND': 32,
}

DOT_NOTE_LENGTHS = {
    'HALF_DOT': 1.33,
    'QUATER_DOT': 2.67,
    'EIGHTH_DOT': 5.33,
    'SIXTEENTH_DOT': 10.67,
    'THIRTY-SECOND_DOT': 21.33
}

def create_note_lengths(quantization = 16, use_dots = True):
    note_lenghts = list(NOTE_LENGTHS.values())
    dot_note_lenghts = list(DOT_NOTE_LENGTHS.values())
    if (use_dots):
        result = (note_lenghts + dot_note_lenghts)
    else:
        result = note_lenghts
    result = sorted(i for i in result if i <= quantization)
    return result

utils = Namespace(
    find_nearest = find_nearest,
    create_note_lengths = create_note_lengths,
)