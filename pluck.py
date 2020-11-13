import numpy as np
from scipy.signal import lfilter
import matplotlib.pyplot as plt
from collections import deque
import pyaudio
import random
random.seed(10)

def pluck(freq, dur, velocity, tone):
    """
    velocity: 0-127
    tone: 0-100
    """
    fs = 44100
    N = round(fs * dur) # no. of samples
    frac_delay = fs/freq - 1
    delay = int(frac_delay) # wavtable length

    # linear interp coefficients
    c1 = frac_delay - delay
    c0 = 1 - c1

    # ring buffer
    rand_init = [(random.random() - 0.5) * velocity/127 for i in range(delay)]

    # tone control param
    a = 1 / (2*np.cos(2*np.pi*freq/fs)+1)
    passes = int(-0.3 * tone + 30); # map tone(0~100) to pass(100~0)
    for i in range(passes):
        rand_init = lfilter([a,a,a], 1, rand_init)    
    
    # kill dc
    for item in rand_init:
        item = item - sum(rand_init)/len(rand_init)
    
    # initiate delayline
    buf = deque(rand_init)

    note = np.zeros(N)
    a0 = 0.05; a1 = 0.9  # 3-point averaging coefficients 

    for i in range(N):
        note[i] = c0 * buf[0] + c1 * buf[-1]
        avg = a0*buf[0] + a1*buf[1] + a0*buf[2]
        buf.append(avg)
        buf.popleft()

    # convert to 16bit, for pyaudio to play
    note = np.array(note * 32767, 'int16') 
    return note

note1 = pluck(282, 5, 100, 100)

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
