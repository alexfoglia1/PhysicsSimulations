import sys
if sys.version_info > (3, 0):
    from tkinter import *
    import tkinter.ttk as ttk
else:
    from Tkinter import *
    import ttk

from time import sleep
from threading import Thread

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
x0p = 1
xfp = SCREEN_WIDTH - 1
y0p = SCREEN_HEIGHT/2 - 1
yfp = SCREEN_HEIGHT
y0p_half = (yfp + y0p)/2
tSpan = int(sys.argv[1])
vSpan = 7000
xScale = SCREEN_WIDTH/tSpan
yScale = (y0p)/vSpan

m = 0.1
k = 5
Fel = lambda x : -k*x
epot = lambda x : 0.5*k*x**2
x0 = 500
y0 = 150
l_air = float(sys.argv[2])
dt = 0.01

callback_args = []

def keydown(e):
    t = Thread(target=mthread)
    t.daemon = True
    t.start()

onExit = lambda e : exit()

def mthread():
    w = callback_args[0]
    w.delete("plot")
    w.delete("mass")
    w.delete("trajectory")
    
    pot = callback_args[1]
    kin = callback_args[2]
    mec = callback_args[3]
        
    t = 0
    x = x0
    y = y0
    ax = 0
    ay = 0
    vx = 0
    vy = 0
    w.create_line(SCREEN_WIDTH/2, 0, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    last_v = vx
    last_t = 0
    last_x = x
    while t < tSpan:
        fx = Fel(x) - l_air*vx
        fy = 0
        ax = fx/m
        ay = fy/m
        vx += ax*dt
        vy += ay*dt
        x += vx*dt
        y += vy*dt
        t += dt
        w.delete("mass")
        w.create_line(SCREEN_WIDTH/2+x, y, SCREEN_WIDTH/2+x+15, y, tag="mass", fill="blue", width=15)
        w.create_line(SCREEN_WIDTH/2+last_x, y, SCREEN_WIDTH/2+x, y, tag="trajectory", fill="blue", width=1)
        
        updatePlot(w, last_t, t, last_v, vx)

        enpot = epot(x)
        enkin = 0.5*m*vx**2
        enmec = enpot + enkin
        pot["value"] = enpot
        kin["value"] = enkin
        mec["value"] = enmec
        
        last_t = t
        last_v = vx
        last_x = x
        
        sleep(dt)

def updatePlot(w, t0, t1, v0, v1):    
    x0 = t0*xScale
    vy0 = y0p_half - v0*yScale
    x1 = t1*xScale
    vy1 = y0p_half - v1*yScale
    w.create_line(x0, vy0, x1, vy1, width=1, tag="plot", fill="red")
    

    
master = Tk()
master.title("Spring Motion")
master.geometry("{}x{}".format(SCREEN_WIDTH,SCREEN_HEIGHT))
w = Canvas(master, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
kin = ttk.Progressbar(w, length=100)
pot = ttk.Progressbar(w, length=100)
mec = ttk.Progressbar(w, length=100)
Label(w, text="Potential E").place(x=SCREEN_WIDTH/4, y=30)
pot.place(x=SCREEN_WIDTH/4, y=60)
Label(w, text="Kinetic E").place(x=2.1*SCREEN_WIDTH/4, y=30)
kin.place(x=2.1*SCREEN_WIDTH/4, y=60)
Label(w, text="Mechanic E").place(x=3*SCREEN_WIDTH/4, y=30)
mec.place(x=3*SCREEN_WIDTH/4, y=60)
maxeval = 1.25*epot(x0)
mec["maximum"] = maxeval
pot["maximum"] = maxeval
kin["maximum"] = maxeval
master.bind("<Return>", keydown)
master.bind("<Escape>", onExit)
w.place(x=0, y=0)
w.create_rectangle(x0p, y0p, xfp, yfp, fill="gray")
w.create_line(x0p, y0p_half, xfp, y0p_half)
callback_args.append(w)
callback_args.append(pot)
callback_args.append(kin)
callback_args.append(mec)
master.mainloop()
