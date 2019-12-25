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
        self.logger = Logger("gena", logging.DEBUG)

        layers = [
            K.layers.LSTM(32, input_shape=(SEQUENCE_LENGTH, NOTES_IN_QUANT), return_sequences=True, dropout=.3),
            K.layers.LSTM(16, return_sequences=False),
            K.layers.Dense(32),
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

        checkpoint_callback = K.callbacks.ModelCheckpoint(filepath=str(checkpoint_path.absolute()), verbose=1,
                                                          save_freq=checkpoint_period)
        # self.fit(dataset, epochs=10, verbose=2, callbacks=[NBatchLogger(), checkpoint_callback])
        self.fit(dataset, epochs=10, verbose=2, callbacks=[NBatchLogger()])

    def generate_midi(self, quants, filename):
        """Generate wav file
        :param int quants: Amount of samples
        :param str filename:
        """
        x = tf.zeros((1, SEQUENCE_LENGTH - 1, NOTES_IN_QUANT))
        x = tf.concat([x, tf.random.uniform((1, 1, NOTES_IN_QUANT))], 0)

        for i in range(quants):
            self.logger.info("Generating {0}/{1}\n".format(i, quants))
            sequence = x[len(x)-1-SEQUENCE_LENGTH:]
            answ = self.predict(sequence)
            # print(answ)
            # x = tf.reshape(answ, (1, self.sample_size, 1))
            x.append(answ)

        encoded = tf.audio.encode_wav(tf.reshape(x, (-1, 1)), 44200)
        tf.io.write_file(filename, encoded)
