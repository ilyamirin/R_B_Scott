from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from keras.layers import Lambda, Input, Dense
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

intermediate_dim = 512
batch_size = 128
latent_dim = 3
epochs = 150

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
    dataset = pypianoroll_midi.load_dataset()
    songs_number = dataset.shape[0]
    song_length_in_bars = dataset.shape[1]
    song_tracks = dataset.shape[2]
    grid_size = dataset.shape[3]
    midi_notes_number = dataset.shape[4]
    dataset = dataset.reshape((songs_number * song_length_in_bars, song_tracks * grid_size * midi_notes_number))
    x_train, x_test = np.array_split(dataset, 2)
    original_dim = x_train.shape[1]

    #normalize
    # x_train = x_train.astype('float32') / midi_notes_number
    # x_test = x_test.astype('float32') / midi_notes_number

    input_shape = (original_dim,)

    # VAE model = encoder + decoder
    # build encoder model
    inputs = Input(shape=input_shape, name='encoder_input')
    x = Dense(intermediate_dim, activation='relu')(inputs)
    z_mean = Dense(latent_dim, name='z_mean')(x)
    z_log_var = Dense(latent_dim, name='z_log_var')(x)

    # use reparameterization trick to push the sampling out as input
    # note that "output_shape" isn't necessary with the TensorFlow backend
    z = Lambda(sampling, output_shape=(latent_dim,), name='z')([z_mean, z_log_var])

    # instantiate encoder model
    encoder = Model(inputs, [z_mean, z_log_var, z], name='encoder')
    encoder.summary()
    plot_model(encoder, to_file='vae_mlp_encoder.png', show_shapes=True)

    # build decoder model
    latent_inputs = Input(shape=(latent_dim,), name='z_sampling')
    x = Dense(intermediate_dim, activation='relu')(latent_inputs)
    outputs = Dense(original_dim, activation='sigmoid')(x)

    # instantiate decoder model
    decoder = Model(latent_inputs, outputs, name='decoder')
    decoder.summary()
    plot_model(decoder, to_file='vae_mlp_decoder.png', show_shapes=True)

    # instantiate VAE model
    outputs = decoder(encoder(inputs)[2])
    vae = Model(inputs, outputs, name='vae_mlp')

    models = (encoder, decoder)

    # VAE loss = mse_loss or xent_loss + kl_loss
    reconstruction_loss = mse(inputs, outputs)

    reconstruction_loss *= original_dim
    kl_loss = 1 + z_log_var - K.square(z_mean) - K.exp(z_log_var)
    kl_loss = K.sum(kl_loss, axis=-1)
    kl_loss *= -0.5
    vae_loss = K.mean(reconstruction_loss + kl_loss)
    vae.add_loss(vae_loss)
    vae.compile(optimizer='adam')
    vae.summary()
    plot_model(vae,
               to_file='vae_mlp.png',
               show_shapes=True)
    # train the autoencoder
    vae.fit(x_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(x_test, None))
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)
    vae.save(os.path.join(MODEL_DIR, 'vae.h5'))
    encoder.save(os.path.join(MODEL_DIR, 'encoder.h5'))
    decoder.save(os.path.join(MODEL_DIR, 'decoder.h5'))
    shapes = {
        'songs_number': songs_number,
        'song_length_in_bars': song_length_in_bars,
        'song_tracks': song_tracks,
        'grid_size': grid_size,
        'midi_notes_number': midi_notes_number,
    }
    shapes_file = open(os.path.join(MODEL_DIR, "shapes.pkl"), "wb")
    pickle.dump(shapes, shapes_file)
    shapes_file.close()

def generate_sample():
    decoder = load_model(os.path.join(MODEL_DIR, 'decoder.h5'))
    shapes_file = open(os.path.join(MODEL_DIR, "shapes.pkl"),"rb")
    shapes =  pickle.load(shapes_file)
    shapes_file.close()
    z_sample = np.zeros((1, latent_dim))
    x_decoded = decoder.predict(z_sample)
    x_decoded = np.around(x_decoded)
    x_decoded = (x_decoded * 64)
    x_decoded = x_decoded.reshape(shapes['song_tracks'], shapes['grid_size'], shapes['midi_notes_number'])
    x_decoded = np.expand_dims(x_decoded, axis=0)
    pypianoroll_midi.write_song_to_midi(x_decoded, "output.mid")
    print(x_decoded)

vae = Namespace(
    train = train,
    generate_sample = generate_sample,
)
