import math
from pathlib import Path
import tensorflow as tf
from tensorflow import keras as K
from .batch_logger import NBatchLogger
from logger import Logger
import logging
from constants import *


class GenaModel(tf.keras.Sequential):
    def __init__(self):
        """Initializes the BDB Gena model.
        """

        super(GenaModel, self).__init__()
        self.log = Logger("gena", logging.DEBUG)

        layers = [
            K.layers.LSTM(256, input_shape=(SEQUENCE_LENGTH, NOTES_IN_QUANT), return_sequences=True, dropout=.3),
            K.layers.LSTM(512, return_sequences=False),
            K.layers.Dense(256),
            K.layers.Dense(NOTES_IN_QUANT)
        ]

        # layers = [
        #     keras.layers.LSTM(100, input_shape=(1, QUANTIZATION * NOTES * TRACKS), return_sequences=True, dropout=.3),
        #     keras.layers.LSTM(10, return_sequences=True, dropout=.3),
        #     keras.layers.LSTM(100, return_sequences=False, dropout=.3),
        #     keras.layers.Dense(QUANTIZATION * NOTES * TRACKS),

        # ]
        for layer in layers:
            self.add(layer)

        self.compile(optimizer='adam', loss='mean_absolute_error')


    def train(self, dataset, checkpoint_path: Path, checkpoint_period: int):
        """Train model"""

        cp_callback = K.callbacks.ModelCheckpoint(filepath=str(checkpoint_path.absolute()), verbose=1, save_freq=checkpoint_period)
        self.fit(dataset, epochs=10, verbose=2, callbacks=[NBatchLogger(), cp_callback])

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
