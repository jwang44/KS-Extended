import pyaudio
from matplotlib import pyplot as plt
import pluck

# note1 = pluck.pluck_note(282, 3, 100, 100, True)
# note2 = pluck.pluck_note(282, 3, 100, 100, True)
chord1 = pluck.pluck_chord(dist=True)
chord2 = pluck.pluck_chord(dist=False)

# fig1 = plt.figure()
# plt.plot(note1)
# fig2 = plt.figure()
# plt.plot(chord1)
# plt.show()

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# open stream (2), 2 is size in bytes of int16
stream = p.open(format=p.get_format_from_width(2),
                channels=1,
                rate=44100,
                output=True)

# play stream (3), blocking call
stream.write(chord1)
stream.write(chord2)

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()
