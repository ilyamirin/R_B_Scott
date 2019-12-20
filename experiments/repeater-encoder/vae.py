from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras.layers import Lambda, Input, Dense, TimeDistributed, Flatten, Reshape, BatchNormalization, Dropout
from keras.models import Model
from keras.losses import mse
from keras.utils import plot_model
from keras import backend as K
from keras.models import load_model

import numpy as np
import matplotlib.pyplot as plt
import pypianoroll_midi
import os
import pickle
from argparse import Namespace


MODEL_DIR = "model"

individual_enc_1_dim = 128
individual_enc_2_dim = 64
global_enc_1_dim = 32
batch_size = 1
latent_dim = 6
epochs = 80

import os
import logger

# reparameterization trick
# instead of sampling from Q(z|X), sample epsilon = N(0,I)
# z = z_mean + sqrt(var) * epsilon
def sampling(args):
    """Reparameterization trick by sampling from an isotropic unit Gaussian.
    # Arguments
        args (tensor): mean and log of variance of Q(z|X)
    # Returns
        z (tensor): sampled latent vector
    """

    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    # by default, random_normal has mean = 0 and std = 1.0
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon


def train():
    Log = logger.Logger('log.txt')
    dataset = pypianoroll_midi.load_dataset()
    songs_number, song_length_in_bars, song_tracks, grid_size, midi_notes_number = dataset.shape
    dataset = dataset.reshape((songs_number, song_length_in_bars, song_tracks * grid_size * midi_notes_number))
    split_proportion = (max(2, round(len(dataset) * 0.2)))
    x_train, x_test = dataset[:-split_proportion], dataset[-split_proportion:]
    pianoroll_dim = x_train.shape[2]

    #normalize
    # x_train = x_train.astype('float32') / midi_notes_number
    # x_test = x_test.astype('float32') / midi_notes_number

    # ENCODER
    inputs = Input(shape=(song_length_in_bars, pianoroll_dim), name='encoder_input')
    x = TimeDistributed(Dense(individual_enc_1_dim, activation='relu'))(inputs)
    x = TimeDistributed(Dense(individual_enc_2_dim, activation='relu'))(x)
    x = Flatten()(x)
    x = Dense(global_enc_1_dim, activation='relu')(x)
    z_mean = Dense(latent_dim, name='z_mean')(x)
    z_log_var = Dense(latent_dim, name='z_log_var')(x)

    z = Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

    encoder = Model(inputs, [z_mean, z_log_var, z], name='encoder')
    plot_model(encoder, to_file='vae_mlp_encoder.png', show_shapes=True)

    # DECODER
    latent_inputs = Input(shape=(latent_dim,), name='z_sampling')
    x = BatchNormalization(momentum=0.9)(latent_inputs) #TODO: fix hardcoded momentum
    x = Dense(global_enc_1_dim, activation='relu')(x)
    x = Dropout(0.1)(x)
    x = Dense((song_length_in_bars*individual_enc_2_dim), activation='relu')(x)
    x = Reshape((song_length_in_bars, individual_enc_2_dim))(x)
    x = TimeDistributed(Dense(individual_enc_1_dim, activation='relu'))(x)
    outputs = Dense(pianoroll_dim, activation='sigmoid')(x)

    decoder = Model(latent_inputs, outputs, name='decoder')
    plot_model(decoder, to_file='vae_mlp_decoder.png', show_shapes=True)

    outputs = decoder(encoder(inputs)[2])
    vae = Model(inputs, outputs, name='vae_mlp')

    # LOSS
    reconstruction_loss = mse(inputs, outputs)
    reconstruction_loss *= pianoroll_dim
    kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
    kl_loss = K.sum(kl_loss, axis=-1)
    kl_loss *= -0.5
    vae_loss = K.mean(reconstruction_loss + kl_loss)
    vae.add_loss(vae_loss)

    vae.compile(optimizer='adam')
    plot_model(vae, to_file='vae_mlp.png', show_shapes=True)
    vae.fit(x_train, epochs=epochs, batch_size=batch_size, validation_data=(x_test, None))

    save_model(encoder, decoder, vae)
    save_track_shape([songs_number, song_length_in_bars, song_tracks, grid_size, midi_notes_number])


def save_model(encoder, decoder, vae):
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)
    vae.save(os.path.join(MODEL_DIR, 'vae.h5'))
    encoder.save(os.path.join(MODEL_DIR, 'encoder.h5'))
    decoder.save(os.path.join(MODEL_DIR, 'decoder.h5'))


def save_track_shape(shape):
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)
    keys = ['songs_number', 'song_length_in_bars', 'song_tracks', 'grid_size', 'midi_notes_number']
    shapes = dict(zip(keys, shape))
    shapes_file = open(os.path.join(MODEL_DIR, "shapes.pkl"), "wb")
    pickle.dump(shapes, shapes_file)
    shapes_file.close()
    Log.close()


def generate_sample():
    decoder = load_model(os.path.join(MODEL_DIR, 'decoder.h5'))
    shapes_file = open(os.path.join(MODEL_DIR, "shapes.pkl"), "rb")
    shapes = pickle.load(shapes_file)
    shapes_file.close()
    z_sample = np.array([np.random.randint(-4, high=4, size=latent_dim)])
    x_decoded = decoder.predict(z_sample)
    medium = (x_decoded.max() + x_decoded.min()) / 2
    x_decoded[x_decoded >= medium] = 1
    x_decoded[x_decoded < medium] = 0
    #x_decoded = np.around(x_decoded)
    x_decoded = (x_decoded * 64)
    x_decoded = x_decoded.reshape(shapes['song_length_in_bars'],
                                  shapes['song_tracks'],
                                  shapes['grid_size'],
                                  shapes['midi_notes_number'])
    pypianoroll_midi.write_song_to_midi(x_decoded, "output.mid")

