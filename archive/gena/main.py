import tensorflow as tf
import argparse
import os
from constants import decode_wav
from model.gena import GenaModel
import logger
# Error without this line.
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

DATA_DIR = './data_dir_wav/'
CHECKPOINT_PERIOD = 1
CHECKPOINT_DIR = "checkpoints/"
CHECKPOINT_FILENAME = "cp-{epoch:04d}.hdf5"
BATCH_SIZE = 10
# size of input
SAMPLING_RATE = 44100
SAMPLE_SIZE = SAMPLING_RATE//100


def create_checkpoint_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Description")
    parser.add_argument('--data_dir', '-D', type=str, default=DATA_DIR)
    parser.add_argument('--checkpoint_period', type=int, default=CHECKPOINT_PERIOD)
    return parser.parse_known_args()


def main():
    known_args, unknown_args = parse_arguments()
    create_checkpoint_dir(CHECKPOINT_DIR)
    logger.configure_logger()

    dataset = tf.data.Dataset.list_files(known_args.data_dir + '*.wav')
    # float32
    dataset = dataset.map(decode_wav)
    # drop sample rates
    dataset = dataset.map(lambda t: t[0])
    dataset = dataset.unbatch()
    dataset = dataset.batch(SAMPLE_SIZE, drop_remainder=True).batch(BATCH_SIZE).prefetch(tf.data.experimental.AUTOTUNE)
    dataset = dataset.zip((dataset, dataset)).take(2)

    gena = GenaModel(SAMPLE_SIZE)
    gena.train(dataset, CHECKPOINT_DIR + CHECKPOINT_FILENAME, CHECKPOINT_PERIOD)

    print('end')


if __name__ == '__main__':
    main()
