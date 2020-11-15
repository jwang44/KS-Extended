import numpy as np
from scipy.signal import lfilter
import matplotlib.pyplot as plt
from collections import deque
import pyaudio
import random
random.seed(10)

def pluck_a_note(freq=440, dur=3, velocity=100, tone=100):
    """
    *obsolete*, use pluck_note instead, which has dist control
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
    passes = int(-0.3 * tone + 30); # map tone(0~100) to pass(30~0)
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

    note = note / max(max(note), abs(min(note))) # normalize
    # convert to 16bit, for pyaudio to play
    note = np.array(note * 32767, 'int16') 
    return note


def pluck_note(freq=440, dur=3, velocity=100, tone=100, dist=True, gain=30):
    """
    velocity: 0-127
    tone: 0-100
    disp: bool
    gain: 
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

    # tone control
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
        note[i] = c0 * buf[0] + c1 * buf[-1] # read from delayline
        note[i] = note[i] * gain

        # distortion control (sample by sample)
        # if dist:
        #     if note[i] > 1:
        #         note[i] = 2/3
        #     elif note[i] < -1:
        #         note[i] = -2/3
        #     else:
        #         note[i] = note[i] - note[i]**3 / 3

        # *0.99 help decay
        avg = (a0*buf[0] + a1*buf[1] + a0*buf[2]) * 0.99
        buf.append(avg) # write into delayline
        buf.popleft()

    note = note / max(max(note), abs(min(note))) # normalize

    # distortion control
    if dist:
        note = note * gain
        dist_note = note - note**3/3
        dist_note[note>1] = 2/3
        dist_note[note<-1] = -2/3
        # convert to 16bit, for pyaudio to play
        note = np.array(dist_note * 32767, 'int16') 
    else:
        note = np.array(note * 32767, 'int16') 

    return note

def pluck_chord(freqs=[70, 120, 140], dur=3, velocity=100, tone=100, dist=False, gain=30):
    fs = 44100
    N = round(dur * fs)
    chord = np.zeros(N)
    for freq in freqs:
        note = pluck_note(freq, dur, velocity, tone, dist=False)
        chord = chord + note
    chord = chord / max(max(chord), abs(min(chord)))

    if dist:
        chord = chord * gain
        dist_chord = chord - chord**3/3
        dist_chord[chord>1] = 2/3
        dist_chord[chord<-1] = -2/3
        # convert to 16bit, for pyaudio to play
        chord = np.array(dist_chord * 32767, 'int16') 
    else:
        chord = np.array(chord * 32767, 'int16') 

    return chord
