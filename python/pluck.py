import numpy as np
from scipy.signal import lfilter
#from collections import deque
import random
random.seed(10)

def pluck(freq=440, dur=6, velocity=127, tone=100, gain=1.5, bend=False, bend_to=500, feedback=False, fb_ratio=0.4):
    """
    freq: fundamental frequency
    dur: note duration in seconds
    velocity: 0-127
    tone: 0-100, controls brightness of the sound
    gain: 1-20, 1 for non-distorted
    bend: Boolean, if false, bend_to has no effect
    bend_to: when bend is True, bend to this frequency
    feedback: Boolean, if false, feedback_ratio has no effect
    fb_ratio: ratio between feedback delay and delay in the string model
    """
    fs = 44100
    N = round(fs * dur) # no. of samples
    delay = fs/freq - 1
    D = int(delay) # wavtable length

    # linear interp coefficients
    c1 = delay - D # fractional part
    c0 = 1 - c1

    # delay line
    #rand_init = random.random()
    rand_init = [(random.random() - 0.5) * 2 * velocity/127 for i in range(D)]
    dl = rand_init

    # kill dc
    for item in rand_init:
        item = item - sum(rand_init)/len(rand_init)

    # feedback delay
    if feedback:
        delay_fb = int(D*fb_ratio)
        dl_fb = np.zeros(delay_fb)
        ptr_fb = 0

    # output buffer
    note = np.zeros(N)
    ptr = 0

    # 3-point averaging coefficients 
    a0 = 0.05; a1 = 0.9  

    # dc-blocking parameters
    dc_block_co = freq/fs/10
    dc_block_a0 = 1/(1+dc_block_co/2)
    dc_block_a1 = -dc_block_a0
    dc_block_b1 = dc_block_a0 * (1 - dc_block_co/2)

    # tone control
    a = 1 / (2*np.cos(2*np.pi*freq/fs)+1)
    passes = int(-0.1 * tone + 10) # map tone(0~100) to pass(30~0)
    for i in range(passes):
        dl = lfilter([a,a,a], 1, dl)
        # if passed througth this, dl will become an np array
        # use tolist() to change it back to list
        dl = dl.tolist()
    
    xm2ave = 0; # x[n-2] for 3-point averaging lp filter
    xm1ave = 0; # x[n-1] for 3-point averaging lp filter
    ym1 = 0;  # y[n-1]

    y_avg_m1 = 0
    y_block_m1 = 0

    if bend:
        if bend_to > freq:
            bend_amount = delay - fs/bend_to
            bend_incre = bend_amount / (0.5*fs)
        else:
            bend_amount = fs/bend_to - delay
            bend_incre = bend_amount / (0.5*fs)
        incre_no = 0

    for i in range(N):
        # pitch bend control
        if bend:
            if bend_to > freq:
                c1 = c1 - bend_incre
                if c1 < 0:
                    c1 = c1 + 1
                    dl.pop() # delayline length decrease by one
                    D = D - 1
                # c0 = 1 - c1
            else:
                c1 = c1 + bend_incre
                if c1 > 1:
                    c1 = c1 - 1
                    dl.append(0) # delayline length increase by one
                    D = D + 1

            c0 = 1 - c1
            incre_no = incre_no + 1

            # if target freq is reached, stop changing delay length
            if incre_no * bend_incre >= bend_amount:
                bend = False

        if ptr > D-1:
            ptr = 0
        x = dl[ptr]
        # 3-point averaging
        y_avg = (a0*x + a1*xm1ave + a0*xm2ave) #* 0.998
        xm2ave = xm1ave
        xm1ave = x
        # dc-blocking
        y_block = dc_block_a0*y_avg + dc_block_a1*y_avg_m1 + dc_block_b1*y_block_m1
        y_avg_m1 = y_avg
        y_block_m1 = y_block

        # linear interpolation
        y = c0 * y_block + c1 * ym1 # read from delayline
        ym1 = y_block

        dl[ptr] = y
        # distortion control (sample by sample)
        y = y * gain
        if y > 1:
            note[i] = 2/3
        elif y < -1:
            note[i] = -2/3
        else:
            note[i] = y - y**3 / 3

        # feedback control
        if feedback:
            # add to string delay line
            dl[ptr] = dl[ptr] + dl_fb[ptr_fb]

            # 0.01 attenuates the output
            dl_fb[ptr_fb] = 0.01*note[i]

            ptr_fb = ptr_fb + 1
            if ptr_fb > delay_fb-1:
                ptr_fb = 0

        ptr = ptr + 1
        if ptr > D-1:
            ptr = 0

    # scale for pyaudio
    note = np.array(note * 32767, 'int16') 
    return note

def pluck_chord(freq=130.8, dur=5, velocity=127, tone=100, gain=1, bend=False, bend_to=500, feedback=False, fb_ratio=0.4):
    """
    freq: fundamental frequency for the root
    dur: note duration in seconds
    velocity: 0-127
    tone: 0-100, controls brightness of the sound
    gain: 1-20, 1 for non-distorted
    bend: Boolean, if false, bend_to has no effect
    bend_to: when bend is True, bend to this frequency
    feedback: Boolean, if false, feedback_ratio has no effect
    fb_ratio: ratio between feedback delay and delay in the string model
    """  
    fs = 44100
    N = round(dur * fs)
    chord = np.zeros(N)

    # just intonation freq ratio 4:5:6, form the chord
    freqs = [0,0,0]
    freqs[0] = freq
    freqs[1] = freq*1.25
    freqs[2] = freq*1.5

    bends_to = [0,0,0]
    bends_to[0] = bend_to
    bends_to[1] = bend_to*1.25
    bends_to[2] = bend_to*1.5

    # pluck every note, if bend=False, the bends_to has no effect
    for freq, bend_to in zip(freqs, bends_to):
        note = pluck(freq, dur, velocity, tone, gain=gain, bend=bend, bend_to=bend_to, feedback=feedback, fb_ratio=fb_ratio)
        chord = chord + note

    chord = chord / max(max(chord), abs(min(chord)))

    # distortion
    chord = chord * gain
    dist_chord = chord - chord**3/3
    dist_chord[chord>1] = 2/3
    dist_chord[chord<-1] = -2/3

    # convert to 16bit, for pyaudio to play
    chord = np.array(dist_chord * 32767, 'int16') 

    return chord
