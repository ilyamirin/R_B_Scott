import tensorflow as tf
import argparse
from model.ops import decode_wav
from model.gena import GenaModel
import model.logger
# Error without this line.
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

DATA_DIR = './data_dir_wav/'
BATCH_SIZE = 10
# size of input
SAMPLING_RATE = 44100
SAMPLE_SIZE = SAMPLING_RATE//100


def parse_arguments():
    parser = argparse.ArgumentParser(description="Description")
    parser.add_argument('--data_dir', '-D', type=str, default=DATA_DIR)
    return parser.parse_known_args()


def main():
    known_args, unknown_args = parse_arguments()
    model.logger.configure_logger()

    dataset = tf.data.Dataset.list_files(known_args.data_dir + '*.wav')
    # float32
    dataset = dataset.map(decode_wav)
    # drop sample rates
    dataset = dataset.map(lambda t: t[0])
    dataset = dataset.unbatch()
    dataset = dataset.batch(SAMPLE_SIZE, drop_remainder=True).batch(BATCH_SIZE).prefetch(tf.data.experimental.AUTOTUNE)
    dataset = dataset.zip((dataset, dataset)).take(2)

    gena = GenaModel(SAMPLE_SIZE)
    gena.train(dataset)
    # 5 seconds
    generate_samples_seconds = SAMPLING_RATE * 5
    gena.generate_wav(generate_samples_seconds, "gen.wav")

    print('end')


if __name__ == '__main__':
    main()
