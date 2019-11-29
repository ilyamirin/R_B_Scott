import tensorflow as tf


class NBatchLogger(tf.keras.callbacks.Callback):
    def __init__(self, display=2):
        self.seen = 0
        self.display = display

    def on_train_batch_end(self, batch, logs={}):
        self.seen += logs.get('size', 0)

        if self.seen % self.display == 0:
            print('\n{0} - Batch Loss: {1}'.format(self.seen, logs['loss']))