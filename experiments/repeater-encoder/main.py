import pypianoroll_midi
import vae

pypianoroll_midi.create_dataset()
vae.train()
vae.generate_sample()