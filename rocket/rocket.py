from time import time, sleep
from math import log

SCREEN_WIDTH = 1200

import sys
if sys.version_info > (3, 0):
    from tkinter import *
    import tkinter.ttk as ttk
else:
    from Tkinter import *
    import ttk

from threading import Thread

callback_args = []

def mthread(positions, speeds, accs, env, dt_s):
    y0 = 150
    i = 0
    for x in positions:
        env.delete("rocket")
        x0_screen = (x + 20) % SCREEN_WIDTH
        xf_screen = x0_screen + 20
        env.create_line(x0_screen, y0, xf_screen, y0, tag="rocket", fill="blue", width=5)
        w.create_text(100, 10, text="Speed {} m/s".format(round(speeds[i],4)), tag="rocket", fill="black", font=("Courier", 14))
        w.create_text(400, 10, text="Acc {} m/s^2".format(round(accs[i],4)), tag="rocket", fill="black", font=("Courier", 14))
        #print("{}".format(x))
        sleep(dt_s)
        i += 1
        
def keydown(e):
    positions = callback_args[0]
    speeds = callback_args[1]
    accs = callback_args[2]
    env = callback_args[3]
    dt_s = callback_args[4]
    t = Thread(target=mthread, args=[positions, speeds, accs, env, dt_s])
    t.daemon = True
    t.start()
        
m_mec_kg = 1e4
m_c_kg = 1e3
u_kms = 1
dt_s = 0.01
dm_dt = 10
vf = lambda vi,u,mi,mf : vi + u*log(mi/mf)

vi_ms = 200
u_ms = u_kms * 1000
mi_kg = m_mec_kg + m_c_kg
vmax = vf(vi_ms, u_ms, mi_kg, m_mec_kg)

actv_ms = vi_ms
actm_kg = mi_kg
act_ref = actm_kg - m_mec_kg
act_t_s = 0
speeds = [vi_ms]
accs = [0]

while act_ref > 0:
    nextm_kg = actm_kg - (dm_dt * dt_s)
    nextv_ms = vf(actv_ms, u_ms, actm_kg, nextm_kg)
    speeds.append(nextv_ms)
    accs.append((nextv_ms - actv_ms) / dt_s)
    actm_kg = nextm_kg
    actv_ms = nextv_ms
    act_ref = actm_kg - m_mec_kg
    act_t_s += dt_s

positions_m = [0]
for v_ms in speeds:
    next_pos = positions_m[-1] + dt_s * v_ms
    positions_m.append(next_pos)

master = Tk()
master.title("Rocket Motion")
master.geometry("{}x{}".format(SCREEN_WIDTH,400))

w = Canvas(master, width=SCREEN_WIDTH, height=300)
master.bind("<Return>", keydown)
w.place(x=0, y=0)

w.create_line(0, 150, 20, 150, tag="rocket", fill="blue", width=5)

callback_args.append(positions_m)
callback_args.append(speeds)
callback_args.append(accs)
callback_args.append(w)
callback_args.append(dt_s)

master.mainloop()

    
