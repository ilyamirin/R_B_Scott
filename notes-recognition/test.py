import sounddevice as sd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import datetime


volume = 1    # range [0.0, 1.0]
fs = 44100      # sampling rate, Hz, must be integer
duration = 1   # in seconds, may be float
f = 520.0        # sine frequency, Hz, may be float
f1 = 228
f2 = 1500

# generate samples, note conversion to float32 array
samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
samples1 = (np.sin(2*np.pi*np.arange(fs*duration)*f1/fs)).astype(np.float32)
samples2 = (np.sin(2*np.pi*np.arange(fs*duration)*f2/fs)).astype(np.float32)

# for paFloat32 sample values must be in range [-1.0, 1.0]

data = volume*(samples + samples1 + samples2)

fig, (time_audiodata_ax, freq_range_ax) = plt.subplots(2, 1)

blk = scipy.blackman(fs)
time_audiodata_ax.plot(data)
freq_range_ax.set_title("freq")
fft = np.abs(np.fft.fft(data * blk, norm='ortho').real ** 2)
fft = fft[:len(fft) // 2]
# fft = fft[:int(len(fft) / 2)]  # keep only first half
freq = np.fft.fftfreq(len(data), 1.0 / fs)
freq = freq[:len(freq) // 2]
# freq = freq[:int(len(freq) / 2)]  # keep only first half
# freqPeak = freq[np.where(fft == np.max(fft))[0][0]] + 1

freq_range_ax.plot(freq, fft)
freqPeak = freq[np.where(fft == np.max(fft))[0][0]] + 1
print(freqPeak)

plt.show()
