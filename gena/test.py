from mido import MidiFile

midi = MidiFile("1.mid")
for msg in midi:
    print(msg)

print("===============")
midi = MidiFile("song.mid")
for msg in midi:
    print(msg)
