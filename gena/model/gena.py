import math
from pathlib import Path
import tensorflow as tf
from tensorflow import keras as K
from .batch_logger import NBatchLogger
from logger import Logger
import logging
from constants import *
from midi_converter import song_to_midi
import numpy as np


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
        self.fit(dataset, epochs=5, verbose=2)

    def generate_midi(self, quants, filename):
        """Generate wav file
        :param int quants: Amount of samples
        :param str filename:
        """
        roll = tf.zeros((SEQUENCE_LENGTH - 1) * NOTES_IN_QUANT)
        roll = tf.concat([roll, tf.random.uniform([NOTES_IN_QUANT])], 0)

        for i in range(quants):
            self.logger.info("Generating {0}/{1}\n".format(i, quants))
            sequence = roll[len(roll) - (SEQUENCE_LENGTH * NOTES_IN_QUANT):]
            sequence = tf.reshape(sequence, (1, SEQUENCE_LENGTH, NOTES_IN_QUANT))
            answ = self.predict(sequence)
            # print(answ)
            # x = tf.reshape(answ, (1, self.sample_size, 1))
            roll = tf.concat([roll, tf.reshape(answ, [-1])], 0)
        roll = tf.reshape(roll, (quants+SEQUENCE_LENGTH, MIDI_INSTRUMENTS_NUMBER, MIDI_NOTES_NUMBER))
        roll = tf.math.scalar_mul(127, roll)
        roll = tf.dtypes.cast(tf.math.round(roll), dtype=tf.int32)
        roll = np.array(roll)
        song_to_midi(roll)
        # encoded = tf.audio.encode_wav(tf.reshape(roll, (-1, 1)), 44200)
        # tf.io.write_file(filename, encoded)
