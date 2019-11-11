import tensorflow as tf
import argparse
import logging
import sys
import librosa

DATA_DIR = './data_dir/'

logger = logging.getLogger("gena")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Description")
    parser.add_argument('--data_dir', '-D', type=str, default=DATA_DIR)
    return parser.parse_args()


def configure_logger():
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)


def path_to_file(path):
    return tf.py_function(lambda x: librosa.load(str(x.numpy(), 'utf-8')), [path], [tf.float32])
    # return path
    # return librosa.load(str(path))


def main():
    args = parse_arguments()
    configure_logger()

    logger.debug("Start preparing dataset")
    dataset = tf.data.Dataset.list_files(args.data_dir + '*mp3')
    logger.debug("Map")
    dataset = dataset.map(path_to_file)
    logger.debug("Finished")
    for d in dataset.take(2):
        print(d[0].numpy().max())
        print('\n')


if __name__ == '__main__':
    main()
