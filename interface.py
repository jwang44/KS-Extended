import pluck
import tkinter as tk
import pyaudio
"""
6 strings interface, no dist, no bend
"""
def change_tone(new_tone):
    tone = new_tone

p = pyaudio.PyAudio()
# def callback(in_data, frame_count, time_info, status):
#     return in_data, pyaudio.paContinue
stream = p.open(format=p.get_format_from_width(2),
                channels=1,
                rate=44100,
                output=True)

window = tk.Tk()
frame_border_effects = {
    "flat": tk.FLAT,
    "sunken": tk.SUNKEN,
    "raised": tk.RAISED,
    "groove": tk.GROOVE,
    "ridge": tk.RIDGE,
}
frame = tk.Frame(relief=tk.GROOVE, borderwidth=5)
label = tk.Label(master=frame,text="Hello GuitarDemo",fg="white",bg="black",width=25,height=2)
entry = tk.Entry(master=frame,fg="yellow", bg="blue", width=25)
tone_scale = tk.Scale(master=frame, from_=10, to=100, orient=tk.HORIZONTAL, label='tone', length=425, showvalue=0)
gain_scale = tk.Scale(master=frame, from_=1, to=100, orient=tk.HORIZONTAL, label='gain', width=25, showvalue=0)


btn1 = tk.Button(
    master=frame,text="pluck",width=25,height=3,
    command=lambda: stream.write(
        pluck.pluck_note(
            freq=82, 
            tone=tone_scale.get(), 
            dist=True,
            gain=gain_scale.get()
            )
        )
    )
btn2 = tk.Button(
    master=frame,text="pluck",width=25,height=3,
    command=lambda: stream.write(pluck.pluck_note(freq=110, tone=tone_scale.get()))
    )
btn3 = tk.Button(
    master=frame,text="pluck",width=25,height=3,
    command=lambda: stream.write(pluck.pluck_note(freq=147, tone=tone_scale.get()))
    )
btn4 = tk.Button(
    master=frame,text="pluck",width=25,height=3,
    command=lambda: stream.write(pluck.pluck_note(freq=196, tone=tone_scale.get()))
    )
btn5 = tk.Button(
    master=frame,text="pluck",width=25,height=3,
    command=lambda: stream.write(pluck.pluck_note(freq=247, tone=tone_scale.get()))
    )
btn6 = tk.Button(
    master=frame,text="pluck",width=25,height=3,
    command=lambda: stream.write(pluck.pluck_note(freq=330, tone=tone_scale.get()))
    )

label.pack()
btn1.pack()
btn2.pack()
btn3.pack()
btn4.pack()
btn5.pack()
btn6.pack()
entry.pack()
tone_scale.pack()
gain_scale.pack()
frame.pack()
window.mainloop()

stream.stop_stream()
stream.close()
p.terminate()
print("closed")
