import tensorflow as tf
import argparse
from pathlib import Path
from model.genb import GenbModel
import model.logger
import numpy as np
from model.ops import *

# Error without this line.
# TODO: check if everything workng witout
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

DATASET_DIR = Path('./dataset/')
CHECKPOINT_PERIOD = 100
CHECKPOINT_DIR = Path('./checkpoints')
CHECKPOINT_FILENAME = "cp-{epoch:04d}.hdf5"
BATCH_SIZE = 1


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
    create_checkpoint_dir(CHECKPOINT_DIR)
    model.logger.configure_logger()
    # dataset structure [song][length_in_bars][quantization=32][note][track] = volume
    np.random.seed(100)
    dataset = np.random.randint(MIN_VOLUME, MAX_VOLUME + 1, (SONGS, LENGTH_IN_BARS, QUANTIZATION, NOTES, TRACKS))
    dataset = dataset.astype(float) / MAX_VOLUME
    dataset = dataset.reshape((SONGS * LENGTH_IN_BARS, 1, QUANTIZATION * NOTES * TRACKS))

    genb = GenbModel()
    genb.train(dataset, BATCH_SIZE, CHECKPOINT_DIR/CHECKPOINT_FILENAME, CHECKPOINT_PERIOD)

    print('end')


if __name__ == '__main__':
    main()
