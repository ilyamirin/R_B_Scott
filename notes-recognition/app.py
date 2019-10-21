import sounddevice as sd
import numpy as np
from numpy.fft import fft, fftfreq, fftshift
import scipy
import matplotlib.pyplot as plt
import datetime

# rate = 44100
rate = 44100
duration = 1200

plt.ion()
fig, (time_audiodata_ax, freq_range_ax) = plt.subplots(2, 1)
plt.show()
blackman = scipy.blackman(rate)

with sd.Stream(channels=1, samplerate=rate) as s:
    playback_speed_multiplier = 1
    for i in range(duration * playback_speed_multiplier):
        print("start reading")
        print(datetime.datetime.now())
        data, b = s.read(int(rate / playback_speed_multiplier))
        # data = data + samples
        # data = data
        print("end reading")
        print(datetime.datetime.now())

        time_audiodata_ax.clear()
        time_audiodata_ax.set_ylim(-1, 1)
        time_audiodata_ax.plot(data)
        time_audiodata_ax.set_title(datetime.datetime.now())

        freq_range_ax.set_title("mem")
        # todo: change


        fft_vals = np.abs(fft(data.flatten() * blackman, norm='ortho').real)**2
        fft_vals = fft_vals[:len(fft_vals) // 2]  # keep only first half
        freq = fftfreq(len(data), 1.0 / rate)
        freq = freq[:len(freq) // 2]  # keep only first half
        freqPeak = freq[np.where(fft_vals == np.max(fft_vals))[0][0]] + 1
        print("peak frequency: %d Hz" % freqPeak)

        freq_range_ax.clear()
        freq_range_ax.plot(freq, fft_vals)
        plt.pause(0.5)

