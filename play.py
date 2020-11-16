import pyaudio
from matplotlib import pyplot as plt
import pluck

# note1 = pluck.pluck_note(282, 3, 100, 100, True)
# note2 = pluck.pluck_note(282, 3, 100, 100, True)
bend1 = pluck.pluck_note_bend(freq=110, dist=False, gain=20, bend=True, bend_to=80)
bend2 = pluck.pluck_note_bend(freq=330, dist=False, gain=20, bend=True, bend_to=300)
#chord2 = pluck.pluck_chord(dist=False)

# fig1 = plt.figure()
# plt.plot(note1)
fig2 = plt.figure()
plt.plot(bend2)
plt.show()

# # instantiate PyAudio (1)
# p = pyaudio.PyAudio()

# # open stream (2), 2 is size in bytes of int16
# stream = p.open(format=p.get_format_from_width(2),
#                 channels=1,
#                 rate=44100,
#                 output=True)

# # play stream (3), blocking call
# stream.write(bend1)
# stream.write(bend2)

# # stop stream (4)
# stream.stop_stream()
# stream.close()

# # close PyAudio (5)
# p.terminate()
