from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras.layers import Lambda, Input, Dense, TimeDistributed, Flatten, Reshape, BatchNormalization, Dropout
from keras.models import Model
from keras.losses import mse, binary_crossentropy
from keras.utils import plot_model
from keras import backend as K
from keras.models import load_model
from keras.backend.tensorflow_backend import set_session
import tensorflow as tf

import os
import logger
import numpy as np
import matplotlib.pyplot as plt
import pypianoroll_midi
from data_generator import DataGenerator
import pickle
from argparse import Namespace


MODEL_DIR = "model"

individual_enc_1_dim = 1024
individual_enc_2_dim = 64
global_enc_1_dim = 32
latent_dim = 150
epochs = 80

Log = logger.Logger('log.txt')

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
    song_length_in_bars, song_tracks, grid_size, midi_notes_number = pypianoroll_midi.get_dataset_shape()
    pianoroll_dim = song_tracks * grid_size * midi_notes_number
    split_proportion = (max(2, round(pypianoroll_midi.get_pianorolls_count() * 0.8)))
    train_generator = DataGenerator(0, split_proportion, (song_length_in_bars, pianoroll_dim))
    test_generator = DataGenerator(split_proportion, pypianoroll_midi.get_pianorolls_count(),
                                   (song_length_in_bars, pianoroll_dim))

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
    xent_loss = binary_crossentropy(inputs, outputs)
    kl_loss = 0.1 * K.mean(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=None)
    vae_loss = xent_loss - kl_loss
    vae.add_loss(vae_loss)

    vae.compile(optimizer='adam')
    plot_model(vae, to_file='vae_mlp.png', show_shapes=True)
    vae.fit_generator(train_generator, epochs=epochs, validation_data=test_generator)

    x_test_encoded = encoder.predict_generator(test_generator)

    save_model(encoder, decoder, vae)
    save_meta({
        'song_length_in_bars': song_length_in_bars,
        'song_tracks': song_tracks,
        'grid_size': grid_size,
        'midi_notes_number': midi_notes_number,
        'min_sample_in_test_data': np.amin(x_test_encoded),
        'max_sample_in_test_data': np.amax(x_test_encoded),
    })

def save_meta(meta):
    #meta is a key-value dict
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)
    meta_file = open(os.path.join(MODEL_DIR, "meta.pkl"), "wb")
    pickle.dump(meta, meta_file)
    meta_file.close()

def save_model(encoder, decoder, vae):
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)
    vae.save(os.path.join(MODEL_DIR, 'vae.h5'))
    encoder.save(os.path.join(MODEL_DIR, 'encoder.h5'))
    decoder.save(os.path.join(MODEL_DIR, 'decoder.h5'))

def generate_sample():
    decoder = load_model(os.path.join(MODEL_DIR, 'decoder.h5'))
    meta_file = open(os.path.join(MODEL_DIR, "meta.pkl"), "rb")
    meta = pickle.load(meta_file)
    meta_file.close()
    print("min:{} max:{}".format(meta['min_sample_in_test_data'], meta['max_sample_in_test_data']))
    z_sample = np.array([np.random.uniform(meta['min_sample_in_test_data'],
                                           high=meta['max_sample_in_test_data'],
                                           size=latent_dim)])
    x_decoded = decoder.predict(z_sample)
    medium = (x_decoded.max() + x_decoded.min()) / 2
    x_decoded[x_decoded >= medium] = 1
    x_decoded[x_decoded < medium] = 0
    #x_decoded = np.around(x_decoded)
    x_decoded = (x_decoded * 64)
    x_decoded = x_decoded.reshape(meta['song_length_in_bars'],
                                  meta['song_tracks'],
                                  meta['grid_size'],
                                  meta['midi_notes_number'])
    pypianoroll_midi.write_song_to_midi(x_decoded, "output.mid")

