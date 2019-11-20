from keras.layers import Input, Dense
from keras.models import Model
from keras import regularizers
import numpy as np
import pypianoroll
import matplotlib.pyplot as plt

dataset = pypianoroll.Multitrack('santana.mid')
# plt.imshow(dataset.tracks[0].pianoroll)
# plt.gray()
# plt.show()
encoding_dim = 32
input_dim = 128
beat_resolution = 24

input_data = np.empty(0)

idx = 0
for track in dataset.tracks:
    t = np.asarray(np.array_split(track.pianoroll, (len(track.pianoroll) / beat_resolution)))
    t = t.astype('float32') / 127
    # for item in t:
    #     plt.imshow(item)
    #     plt.gray()
    #     plt.show()
    t = t.reshape((len(t), np.prod(t.shape[1:])))
    if (idx == 0):
        input_data = t
    else:
        input_data = np.concatenate((input_data, t))
    idx += 1

input_data, test_data = np.array_split(input_data, 2)

input_layer = Input(shape=(input_dim*beat_resolution,))
encoded = Dense(encoding_dim, activation='relu', activity_regularizer=regularizers.l1(10e-5))(input_layer)
decoded = Dense(input_dim*beat_resolution, activation='sigmoid')(encoded)

autoencoder = Model(input_layer, decoded)
encoder = Model(input_layer, encoded)
encoded_input = Input(shape=(encoding_dim,))
decoder_layer = autoencoder.layers[-1]
decoder = Model(encoded_input, decoder_layer(encoded_input))
autoencoder.compile(optimizer='adam', loss='mean_squared_error')


# from keras.datasets import mnist
# (x_train, _), (x_test, _) = mnist.load_data()
#
# x_train = x_train.astype('float32') / 255
# x_test = x_test.astype('float32') / 255
# x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
# x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))

autoencoder.fit(input_data, input_data,
                epochs=1,
                batch_size=8,
                shuffle=True,
                validation_data=(test_data, test_data))

decoded_imgs = autoencoder.predict(input_data)

iterations = list(np.random.random_integers(0, input_data.shape[0], 10))
n = 10  # how many digits we will display
plt.figure(figsize=(20, 4))
for i in range(10):
    # display original
    ax = plt.subplot(2, n, i + 1)
    plt.imshow(input_data[iterations[i]].reshape(beat_resolution, input_dim))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # display reconstruction
    ax = plt.subplot(2, n, i + 1 + n)
    plt.imshow(decoded_imgs[iterations[i]].reshape(beat_resolution, input_dim))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()