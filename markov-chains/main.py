import mido
import markovify
import pygame.midi
import time

mid = mido.MidiFile('song.mid')
notes = []
# outport = mido.open_output()
for msg in mid:
    print(msg)
    if (msg.type == 'note_on'):
        # outport.send(msg)
        notes.append((msg.note, round(msg.time,2)))
    if (msg.type == 'note_off'):
        t = list(notes[len(notes)-1])
        t[1] = round(msg.time,2)
        notes[len(notes)-1] = tuple(t)
print(notes)
# outport.close()

text_model = markovify.Chain([notes], state_size=4)
generated = text_model.walk()
print(generated)

pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)

for note, length in generated:
    player.note_on(note, 127)
    time.sleep(length*2)
    player.note_off(note, 127)

del player
pygame.midi.quit()