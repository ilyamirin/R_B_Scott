import sounddevice as sd
import numpy as np

rate = 44100
sec = 3

# duration = 10.5  # seconds
# myrecording = sd.rec(int(sec * rate), samplerate=rate, channels=1)
# print("end recording")
# sd.wait()
data = np.random.rand(rate*sec)
data = 0.5**6 * data

sd.play(data, rate)
sd.wait()