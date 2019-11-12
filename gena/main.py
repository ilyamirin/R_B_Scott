import tensorflow as tf
from timeit import default_timer as timer
import argparse
import logging
import sys
from tensorflow import keras
from keras.backend.tensorflow_backend import set_session

# Error without this line.
physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

DATA_DIR = './data_dir_wav/'
# tracks to process simultaneously
BATCH_SIZE = 3
# size of input
SAMPLE_SIZE = 44200//100

logger = logging.getLogger("gena")


class NBatchLogger(tf.keras.callbacks.Callback):
    def __init__(self, display=100):
        '''
        display: Number of batches to wait before outputting loss
        '''
        self.seen = 0
        self.display = display

    def on_train_batch_end(self, batch, logs={}):
        self.seen += logs.get('size', 0)
        if self.seen % self.display == 0:
            print('\n{0} - Batch Loss: {1}'.format(self.seen, self.params['metrics']['loss']))

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
    start = 0
    end = 0
    for d in dataset.take(100):
        end = timer()
        print(end - start)
        print("hello")
        start = timer()


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
    dataset = dataset.batch(SAMPLE_SIZE, drop_remainder=True).batch(BATCH_SIZE).repeat(10).prefetch(tf.data.experimental.AUTOTUNE)
    dataset = dataset.zip((dataset, dataset))

    model = keras.Sequential([
        keras.layers.LSTM(SAMPLE_SIZE, input_shape=(None, 1), return_sequences=True, dropout=.3),
        keras.layers.LSTM(SAMPLE_SIZE // 2, return_sequences=True, dropout=.3),
        keras.layers.LSTM(SAMPLE_SIZE // 4, return_sequences=True, dropout=.3),
        keras.layers.LSTM(SAMPLE_SIZE // 2, return_sequences=True, dropout=.3),
        keras.layers.Dense(SAMPLE_SIZE),
    ])

    out_batch = NBatchLogger(display=1)

    model.compile(optimizer='adam', loss='mean_absolute_error')
    model.fit(dataset, epochs=10000, verbose=2, steps_per_epoch=1, callbacks=[])


if __name__ == '__main__':
    main()
