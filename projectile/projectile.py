import sys
if sys.version_info > (3, 0):
    from tkinter import *
    import tkinter.ttk as ttk
else:
    from Tkinter import *
    import ttk
import time
from math import sin,cos,acos,asin
from threading import Thread

callback_args = []
wheight = 650
wwidth = 1300
g = 9.80665
s = lambda a,v0,s0,t : 0.5*a*(t**2) + v0*t + s0
v = lambda a,v0,t : a*t + v0
ecin = lambda m,v : 0.5*m*v**2
epot = lambda m,g,h : m*g*h
x0 = 20
y0 = 490
size = 15
v0x = 60
v0y = -80
time_scale = 0.2
token = True

def motion(w, x0, y0, size, v0x, v0y, mecpbar, potpbar, kinpbar):
    global token
    if not token:
        return
    
    token = False
    ax = 0
    ay = g
    x = x0
    y = y0
    vx = v0x
    vy = v0y
    t0 = time.time()
    
    while y <= y0:
        t = (time.time() - t0)/time_scale
        x = s(ax,v0x,x0,t)
        y = s(ay,v0y,y0,t)
        vx = v(ax,v0x,t)
        vy = v(ay,v0y,t)
        kin = ecin(1, (vx**2 + vy**2)**0.5)
        pot = epot(1, g, -(y-y0))
        draw(w, t, x, y, vx, vy, pot, kin, mecpbar, potpbar, kinpbar)
    
    token=True
    draw(w, t, x0, y0, v0x, v0y, 0, 0, mecpbar, potpbar, kinpbar)
    w.delete("text")

def keydown(e):
    w = callback_args[0]
    x0 = callback_args[1]
    y0 = callback_args[2]
    size = callback_args[3]
    v0x = callback_args[4]
    v0y = callback_args[5]
    mecpbar = callback_args[6]
    potpbar = callback_args[7]
    kinpbar = callback_args[8]
    
    t = Thread(target=motion, args=[w,x0,y0,size,v0x,v0y,mecpbar,potpbar,kinpbar])
    t.daemon = True
    t.start()

def initprojectile(v0ydelta=1, v0xdelta=1):
    w.delete("proj")
    w.delete("traj")

    x0 = callback_args[1]
    y0 = callback_args[2]
    v0x = callback_args[4]
    v0y = callback_args[5]
    mecpbar = callback_args[6]
    potpbar = callback_args[7]
    kinpbar = callback_args[8]

    v0x += v0xdelta
    v0y += v0ydelta
    
    callback_args[4] = v0x
    callback_args[5] = v0y
    
    phi0 = acos(v0x/((v0x**2 + v0y**2)**0.5))
    w.create_line(x0, y0, x0 + size*cos(phi0), y0 - size*sin(phi0), fill="blue", tag="proj", width=size/3)
    
    if v0x != 0:
        t_max_x = 2*(-v0y)/g
        max_x = s(0, v0x, x0, t_max_x)
        xcoords = []
        ycoords = []
        x = x0
        while x <= max_x:
            xcoords.append(x)
            t_of_x = (x - x0)/v0x
            y_of_t = s(g, v0y, y0, t_of_x)
            ycoords.append(y_of_t)
            x += (max_x - x0)/wwidth 
        for i in range(0, len(xcoords) - 1):
            w.create_line(xcoords[i], ycoords[i], xcoords[i+1], ycoords[i+1], fill="red", width=1, tag="traj")
    maxeval = epot(1,g,x0) + ecin(1, (v0x**2 + v0y**2)**0.5)
    mecpbar["maximum"] = maxeval
    potpbar["maximum"] = maxeval
    kinpbar["maximum"] = maxeval

def mousewheelup(e):
    initprojectile(-1, 0)

def mousewheeldown(e):
    initprojectile(1, 0)
    
def mousemotion(e):
    if len(callback_args) < 10:
        callback_args.append(e.x)
    else:
        direction = 1 if (e.x - callback_args[9]) >= 0 else -1
        callback_args[9] = e.x
        initprojectile(0, direction)

def mouserelease(e):
    if len(callback_args) == 10:
        callback_args.remove(callback_args[9])

def draw(w, t, x, y, vx, vy, pot, kin, mecpbar, potbbar, kinpbar):
    mec = pot + kin
    w.delete("proj")
    w.delete("timetext")
    w.delete("text")
    w.create_text(200,50, text="Speed x: {} m/s\nSpeed y: {} m/s\nSpeed magnitude: {} m/s\nKinetic energy: {} J\nPotential energy: {} J\nMechanical energy: {} J"\
    .format(round(vx,5), round(-vy,5), round((vx**2 + vy**2)**0.5,5), round(kin,5), round(pot,5), round(mec,5)), tag="text", font=("Courier", 8))
    w.create_text(w.winfo_width()-100, 60, tag="timetext", text="t = {} s".format(round(t,5)), font=("Courier", 10))

    phi0 = acos(vx/((vx**2 + vy**2)**0.5))
    if vy >= 0:
        phi0 = -phi0
    w.create_line(x, y, x + size*cos(phi0), y - size*sin(phi0), fill="blue", tag="proj", width=size/3)

    w.create_oval(x-2, y0-2, x+2, y0+2, tag="proj", fill="red")
    w.create_line(x, y0, x, y, tag="proj", dash=(1,3), fill="red")
    w.create_oval(x0-2, y-2, x0+2, y+2, tag="proj", fill="blue")
    w.create_line(x0, y, x, y, tag="proj", dash=(1,3), fill="blue")

    mecpbar["value"] = mec
    potpbar["value"] = pot
    kinpbar["value"] = kin
    time.sleep(0.01)
    
master = Tk()
master.title("Projectile Motion")
master.geometry("{}x{}".format(wwidth,wheight))

ttk.Label(master, text="Mechanical Energy").place(x=10,y=30)
mecpbar = ttk.Progressbar(master, orient="horizontal", length=200)
mecpbar.place(x=160,y=30)

ttk.Label(master, text="Potential Energy").place(x=400,y=10)
potpbar = ttk.Progressbar(master, orient="horizontal", length=200)
potpbar.place(x=530,y=10)

ttk.Label(master, text="Kinetic Energy").place(x=400,y=50)
kinpbar = ttk.Progressbar(master, orient="horizontal", length=200)
kinpbar.place(x=530,y=50)

w = Canvas(master, width=wwidth, height=wheight-100)

w.create_line(x0, y0, wwidth, y0)
w.create_line(x0, y0, x0, 0)

w.create_text(x0 - 5, y0 + 5, text="0", font=("Courier", 6))

abscissa = x0
while abscissa < 1000:
    w.create_line(abscissa, y0, abscissa, y0-5)
    abscissa += 10
    if abscissa % 20 == 0:
        w.create_text(abscissa, y0+5, text="{}".format(abscissa - 20), font=("Courier", 6))
        
ordinate = y0
while y0-ordinate <= 450:
    w.create_line(x0, ordinate, x0+5, ordinate)
    ordinate -= 10
    if ordinate % 20 == 0:
        w.create_text(x0 - 10, ordinate, text="{}".format(y0-ordinate), font=("Courier", 6))
        
w.create_line(wwidth-50, 20, wwidth-60, 20)
w.create_line(wwidth-50, 23, wwidth-50, 17)
w.create_line(wwidth-60, 23, wwidth-60, 17)

w.create_line(wwidth-75, 20, wwidth-75, 30)
w.create_line(wwidth-72, 20, wwidth-76, 20)
w.create_line(wwidth-72, 30, wwidth-76, 30)

w.create_text(wwidth-55, 10, text="10m", font=("Courier", 8))
w.create_text(wwidth-90, 25, text="10m", font=("Courier", 8))

callback_args.append(w)
callback_args.append(x0)
callback_args.append(y0)
callback_args.append(size)
callback_args.append(v0x)
callback_args.append(v0y)
callback_args.append(mecpbar)
callback_args.append(potpbar)
callback_args.append(kinpbar)

w.place(x=10, y=80)
master.bind("<Return>", keydown)
master.bind("<B1-Motion>", mousemotion)
master.bind("<ButtonRelease-1>", mouserelease)
master.bind("<Button-4>", mousewheelup)
master.bind("<Button-5>", mousewheeldown)


initprojectile(0, 0)
w.create_text(wwidth-100, 60, tag="timetext", text="t = 0.00000 s", font=("Courier", 10))
master.mainloop()
