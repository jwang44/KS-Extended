import pyaudio
import pluck

note1 = pluck.pluck_a_note(282, 5, 100, 100)

# fig = plt.figure()
# plt.plot(note1)
# plt.show()

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# open stream (2), 2 is size in bytes of int16
stream = p.open(format=p.get_format_from_width(2),
                channels=1,
                rate=44100,
                output=True)

# play stream (3), blocking call
stream.write(note1)

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()