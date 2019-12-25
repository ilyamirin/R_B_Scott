import tensorflow as tf
import argparse
from pathlib import Path

from midi_converter import midi_to_song
from model.gena import GenaModel
from logger import Logger
import logging
import numpy as np
from constants import *

# Error without this line.
# TODO: check if everything working without
# physical_devices = tf.config.experimental.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], True)

DATASET_DIR = Path('./dataset/')
CHECKPOINT_PERIOD = 100
CHECKPOINT_DIR = Path('./checkpoints')
CHECKPOINT_FILENAME = "cp-{epoch:04d}.hdf5"
BATCH_SIZE = 1

log = Logger("main", logging.DEBUG)


def create_checkpoint_dir(path: Path):
    if not path.exists():
        path.mkdir()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Description")
    parser.add_argument('--data_dir', '-D', type=str, default=DATASET_DIR)
    parser.add_argument('--checkpoint_period', type=int, default=CHECKPOINT_PERIOD)
    return parser.parse_known_args()


def main():
    known_args, unknown_args = parse_arguments()
    # create_checkpoint_dir(CHECKPOINT_DIR)
    # dataset structure [song][length_in_bars][quantization=32][note][track] = volume
    # np.random.seed(100)
    # dataset = np.random.randint(MIN_VOLUME, MAX_VOLUME + 1, (SONGS, LENGTH_IN_BARS, QUANTIZATION, NOTES, TRACKS))
    # dataset = dataset.astype(float) / MAX_VOLUME
    # dataset = dataset.reshape((SONGS * LENGTH_IN_BARS, 1, QUANTIZATION * NOTES * TRACKS))

    # roll = [[[0 for _ in range(MIDI_NOTES_NUMBER)] for _ in range(MIDI_INSTRUMENTS_NUMBER)] for _ in range(total_quants)]
    # in quants
    #
    # x = song.unbatch()
    # x = x.unbatch()
    # x = x.window(NOTES_IN_QUANT * SEQUENCE_LENGTH, NOTES_IN_QUANT, drop_remainder=True)
    # x = x.unbatch().batch(NOTES_IN_QUANT).batch(SEQUENCE_LENGTH)
    #
    # y = song.skip(SEQUENCE_LENGTH).unbatch().unbatch().batch(NOTES_IN_QUANT)
    # dataset = tf.data.Dataset.zip((x, y))
    #
    # (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    # train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
    #
    # # dataset = tf.data.Dataset.from_tensor_slices((x, y)).batch(1)
    # s = tf.data.experimental.get_single_element(x)

    roll = (np.array(midi_to_song(Path('song.mid')), dtype=np.float32) / 128).flatten()
    x = []
    y = []
    for i in range(0, len(roll), NOTES_IN_QUANT):
        right_border = i + SEQUENCE_LENGTH * NOTES_IN_QUANT
        if right_border + 1 + NOTES_IN_QUANT >= len(roll):
            break
        x.append(roll[i:right_border])
        y.append(roll[right_border+1:right_border+1+NOTES_IN_QUANT])

    x = np.array(x)
    y = np.array(y)
    # x = tf.data.Dataset.from_tensor_slices(x).batch

    x = np.reshape(x, (x.shape[0], 1, SEQUENCE_LENGTH, NOTES_IN_QUANT))
    gena = GenaModel()
    dataset = tf.data.Dataset.from_tensor_slices((x, y))
    gena.train(dataset, CHECKPOINT_DIR/CHECKPOINT_FILENAME, CHECKPOINT_PERIOD)
    gena.generate_midi(10, "result.mid")
    print('end')


if __name__ == '__main__':
    main()
