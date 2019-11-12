import tensorflow as tf
import argparse
import logging
import sys
import librosa

DATA_DIR = './data_dir_wav/'
BATCH_SIZE = 32
# size of input
SAMPLE_SIZE = 44200

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
    return tf.audio.decode_wav(file, desired_channels=1)


def print_dataset(dataset):
    print("Printing " + str(dataset))
    for d in dataset.take(100):
        print(1)
    # print('------------------------------')
    # print('\n\n')


def main():
    args = parse_arguments()
    configure_logger()

    dataset = tf.data.Dataset.list_files(args.data_dir + '*.wav')
    # float32
    dataset = dataset.map(decode_wav)
    # drop sample rate
    dataset = dataset.map(lambda t: t[0])
    dataset = dataset.unbatch()
    dataset = dataset.batch(SAMPLE_SIZE).batch(BATCH_SIZE, drop_remainder=True).prefetch(10)
    print_dataset(dataset)


if __name__ == '__main__':
    main()
