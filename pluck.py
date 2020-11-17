import numpy as np
from scipy.signal import lfilter
from collections import deque
import random
random.seed(10)

def pluck_note(freq=440, dur=3, velocity=100, tone=100, dist=True, gain=30, bend=True, bend_to=500):
    """
    velocity: 0-127
    tone: 0-100
    dist: bool
    gain: gain amount
    """
    fs = 44100
    N = round(fs * dur) # no. of samples
    frac_delay = fs/freq - 1
    delay = int(frac_delay) # wavtable length

    # linear interp coefficients
    c1 = frac_delay - delay # fractional part
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
    y = 0; ym1 = 0

    if bend:
        if bend_to > freq:
            bend_amount = frac_delay - fs/bend_to
            bend_incre = bend_amount / (0.5*fs)
        else:
            bend_amount = fs/bend_to - frac_delay
            bend_incre = bend_amount / (0.5*fs)
        incre_no = 0

    for i in range(N):

        # pitch bend control
        if bend:
            if bend_to > freq:
                c1 = c1 - bend_incre
                if c1 < 0:
                    c1 = c1 + 1
                    buf.popleft() # delayline length decrease by one
                c0 = 1 - c1
            else:
                c1 = c1 + bend_incre
                if c1 > 1:
                    c1 = c1 - 1
                    buf.append(0) # delayline length increase by one
                    # produce glitch in sound
            incre_no = incre_no + 1

            if incre_no * bend_incre >= bend_amount:
                bend = False

        # *0.99 help decay
        ym1 = y
        y = (a0*buf[0] + a1*buf[1] + a0*buf[2]) * 0.998
        note[i] = c0 * y + c1 * ym1 # read from delayline

        buf.append(note[i]) # write into delayline
        buf.popleft()

        # distortion control (sample by sample)
        note[i] = note[i] * gain
        if dist:
            if note[i] > 1:
                note[i] = 2/3
            elif note[i] < -1:
                note[i] = -2/3
            else:
                note[i] = note[i] - note[i]**3 / 3

    note = note / max(max(note), abs(min(note))) # normalize

    # distortion control
    # if dist:
    #     note = note * gain
    #     dist_note = note - note**3/3
    #     dist_note[note>1] = 2/3
    #     dist_note[note<-1] = -2/3
    #     # convert to 16bit, for pyaudio to play
    #     note = np.array(dist_note * 32767, 'int16')
    # else:
    #     note = np.array(note * 32767, 'int16') 
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

def pluck_note_bend(
    freq=440, dur=5, velocity=100, tone=100, dist=False, gain=30, 
    bend=True, bend_to=450, 
    feedback=True, feedback_delay=0.4
    ):
    """
    OBSOLETE, delay line interpolation is wrong, use pluck_note
    velocity: 0-127
    tone: 0-100
    dist: bool
    gain: 
    """
    fs = 44100
    N = round(fs * dur) # no. of samples
    frac_delay = fs/freq - 1
    delay = int(frac_delay) # wavtable length

    # linear interp coefficients
    c1 = frac_delay - delay # fractional part
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

    # initiate feedback delayline
    if feedback:
        fb_delay = int(feedback_delay * delay)
        fb_init = np.zeros(fb_delay)
        fb_buf = deque(fb_init)

    note = np.zeros(N)
    a0 = 0.05; a1 = 0.9  # 3-point averaging coefficients 

    if bend:
        if bend_to > freq:
            bend_amount = frac_delay - fs/bend_to
            bend_incre = bend_amount / (0.5*fs)
        else:
            bend_amount = fs/bend_to - frac_delay
            bend_incre = bend_amount / (0.5*fs)
        incre_no = 0

    for i in range(N):
        note[i] = c0 * buf[0] + c1 * buf[-1] # read from delayline

        # pitch bend control
        if bend:
            if bend_to > freq:
                c1 = c1 - bend_incre
                if c1 < 0:
                    c1 = c1 + 1
                    buf.popleft() # delayline length decrease by one
                c0 = 1 - c1
            else:
                c1 = c1 + bend_incre
                if c1 > 1:
                    c1 = c1 - 1
                    buf.append(buf[0]) # delayline length increase by one
                    # produce glitch in sound
            incre_no = incre_no + 1

            if incre_no * bend_incre >= bend_amount:
                bend = False

        # *0.995 help decay
        avg = (a0*buf[0] + a1*buf[1] + a0*buf[2]) * 0.995

        buf.append(avg) # write into delayline
        buf.popleft()

        if feedback:
            buf[0] = buf[0]+fb_buf[0]
            fb_buf.append(note[i] * 0.01)
            fb_buf.popleft()

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

    # print("tone: ", tone)
    return note
