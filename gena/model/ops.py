import tensorflow as tf


def decode_wav(filename):
    file = tf.io.read_file(filename)
    return tf.audio.decode_wav(file, desired_channels=1)
