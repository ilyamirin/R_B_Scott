import tensorflow as tf
import argparse
import logging
import sys
import librosa

DATA_DIR = './data_dir_wav/'

logger = logging.getLogger("gena")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Description")
    parser.add_argument('--data_dir', '-D', type=str, default=DATA_DIR)
    return parser.parse_args()


def configure_logger():
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)


def decode_wav(filename):
    file = tf.io.read_file(filename)
    return tf.audio.decode_wav(file)


def main():
    args = parse_arguments()
    configure_logger()

    dataset = tf.data.Dataset.list_files(args.data_dir + '*.wav')
    dataset = dataset.map(decode_wav)
    for d in dataset.take(5):
        print(d[0])
        print('\n')


if __name__ == '__main__':
    main()
