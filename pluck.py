import numpy as np
import matplotlib.pyplot as plt
from collections import deque
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
    for item in rand_init:
        item = item - sum(rand_init)/len(rand_init)
    buf = deque(rand_init)
    note = np.zeros(N)
    a0 = 0.05; a1 = 0.9  # 3-point averaging coefficients 

    for i in range(N):
        note[i] = c0 * buf[0] + c1 * buf[-1]
        avg = a0*buf[0] + a1*buf[1] + a0*buf[2]
        buf.append(avg)
        buf.popleft()
    return note

note1 = pluck(441, 5, 127, 0)
fig = plt.figure()
plt.plot(note1)
# plt.plot(range(len(note1)), note1)
plt.show()