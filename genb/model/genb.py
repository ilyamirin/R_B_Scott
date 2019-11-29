import math
import tensorflow as tf
from tensorflow import keras
from .batch_logger import NBatchLogger
from .logger import logger


class GenbModel(tf.keras.Sequential):
    def __init__(self, sample_size):
        """Initializes the BDB Genb model.

        :param int sample_size:how many data points to take for the input
        """

        super(GenbModel, self).__init__()
        self.sample_size = sample_size

        layers = [
            keras.layers.LSTM(sample_size, input_shape=(None, 1), return_sequences=True, dropout=.3),
            keras.layers.LSTM(sample_size // 4, return_sequences=True, dropout=.3),
            keras.layers.LSTM(sample_size // 16, return_sequences=True, dropout=.3),
            keras.layers.LSTM(sample_size // 4, return_sequences=False, dropout=.3),
            keras.layers.Dense(sample_size)
        ]
        self.compile(optimizer='adam', loss='mean_absolute_error')

        for layer in layers:
            self.add(layer)

    def train(self, dataset, checkpoint_path, checkpoint_period):
        """Train model"""

        cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path, verbose=1, save_weights_only=True,
                                                         save_freq=checkpoint_period)
        self.fit(dataset, epochs=1, verbose=2, steps_per_epoch=None, callbacks=[NBatchLogger(), cp_callback])

    def generate_midi(self, samples, filename):
        """Generate wav file
        :param int samples: Amount of samples
        :param str filename:
        """

        x = tf.random.uniform((1, self.sample_size, 1))
        x = tf.data.Dataset.from_tensors(x)
        res = []
        buckets_to_gen = math.ceil(samples / self.sample_size)
        for i in range(buckets_to_gen):
            logger.info("Generating {0}/{1}\n".format(i*self.sample_size, samples))
            answ = self.predict(x)
            # print(answ)
            x = tf.reshape(answ, (1, self.sample_size, 1))
            res.append(x)

        encoded = tf.audio.encode_wav(tf.reshape(res, (-1, 1)), 44200)
        tf.io.write_file(filename, encoded)
