import sys
if sys.version_info > (3, 0):
    from tkinter import *
    import tkinter.ttk as ttk
else:
    from Tkinter import *
    import ttk
import time
from math import sin,cos,acos,asin,exp,log,atan
from threading import Thread

callback_args = []
simulation_states=[]
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
v0y = -75
b_air = 0.02
b=b_air
time_scale = 0.2
token = True
air = False

def motion(w, x0, y0, size, v0x, v0y, mecpbar, potpbar, kinpbar):
    global token
    if not token:
        return
    token = False
    
    w.delete("state")
    mec0 = ecin(1, (v0x**2 + v0y**2)**0.5)
    ax = 0
    ay = g
    x = x0
    y = y0
    vx = v0x
    vy = v0y
    simulation_states = []
    b = float(callback_args[9].get())
    tau = 1/b
    vL = g*tau
    v_euler = [y0]
    last_t = 0
    is_air = air
    iterations = 0
    t0 = time.time()

    while y <= y0:
        t = (time.time() - t0)/time_scale
        h = (t-last_t)
        last_t = t
        if is_air:
            x = 1/b * v0x*(1-exp(-b * t)) + x0
            vx = v0x*exp(-b * t)
            vy = vL - (vL-v0y)*exp(-t/tau)
            v_euler.append(v_euler[-1] + h*vy)
            y = v_euler[-1]
        else:
            x = s(ax,v0x,x0,t)
            y = s(ay,v0y,y0,t)
            vx = v(ax,v0x,t)
            vy = v(ay,v0y,t)
        kin = ecin(1, (vx**2 + vy**2)**0.5)
        pot = epot(1, g, -(y-y0))
        mec = pot + kin
        loss = mec0 - mec
        record_state(simulation_states, t, x, y, vx, vy, pot, kin, mec, loss)
        draw(w, t, x, y, vx, vy, pot, kin, mec, loss, mecpbar, potpbar, kinpbar, simulation_states)
        iterations += 1
        time.sleep(0.01)
        
    token=True
    #draw(w, t, x0, y0, v0x, v0y, 0, 0, 0, 0, mecpbar, potpbar, kinpbar) DRAW MAIN RESULTS AS SPEED DIFFERENCE HERE
    
def record_state(simulation_states, t, x, y, vx, vy, pot, kin, mec, loss):
    simulation_state = {}
    simulation_state['t'] = t
    simulation_state['x'] = x
    simulation_state['y'] = y
    simulation_state['vx'] = vx
    simulation_state['vy'] = vy
    simulation_state['pot'] = pot
    simulation_state['kin'] = kin
    simulation_state['mec'] = mec
    simulation_state['loss'] = loss
    
    simulation_states.append(simulation_state)

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
    if len(callback_args) < 11:
        callback_args.append(e.x)
    else:
        direction = 1 if (e.x - callback_args[10]) >= 0 else -1
        callback_args[10] = e.x
        initprojectile(0, direction)

def mouserelease(e):
    if len(callback_args) == 11:
        callback_args.remove(callback_args[10])

def dumpswitched():
    global air
    air = not air
    bField = callback_args[9]
    bField.state(['{}disabled'.format('!' if air else '')])

def draw(w, t, x, y, vx, vy, pot, kin, mec, loss, mecpbar, potbbar, kinpbar, simulation_states=None):
    w.delete("proj")
    w.delete("timetext")
    w.delete("text")
    
    w.create_text(200,50, text="Speed x: {} m/s\nSpeed y: {} m/s\nSpeed magnitude: {} m/s\nKinetic energy: {} J\nPotential energy: {} J\nMechanical energy: {} J\nEnergy loss: {} J"\
    .format(round(vx,5), round(-vy,5), round((vx**2 + vy**2)**0.5,5), round(kin,5), round(pot,5), round(mec,5), round(loss,5)), tag="text", font=("Courier", 8))
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
    
    if simulation_states is not None:
        if len(simulation_states) == 1:
            create_plot(w)
        else:
            update_plot(w, simulation_states)
    
def create_plot(w):
    update_plot(w, None, True)    
    
def update_plot(w, simulation_states, create=False):
    px0 = 2*w.winfo_width()/3
    py0 = w.winfo_height()/3.5
    s0 = -100
    sF = 100
    pyf = py0 - s0 + sF
    pxf = w.winfo_width() - 20
    t0 = 0
    tF = 20
    x_scale = (pxf-px0)/(tF-t0)
    y_scale = (pyf-py0)/(sF-s0)
    vycol = "red"
    vxcol = "blue"
    wcol = "magenta"
    vmcol = "green"

    if create:
        w.create_rectangle(px0, py0, pxf, pyf, fill="white", tag="plot")
        w.create_line(px0, py0 + (pyf-py0)/2, pxf, py0 + (pyf-py0)/2, tag="plot")
        w.create_text(pxf-50, py0+5, text="Speed x", fill=vxcol, font=("Courier", 8))
        w.create_text(pxf-50, py0+17, text="Speed y", fill=vycol, font=("Courier", 8))
        w.create_text(pxf-50, py0+29, text="||Speed||", fill=vmcol, font=("Courier", 8))
        w.create_text(pxf-50, py0+41, text="Energy loss/100", fill=wcol, font=("Courier", 8))
        abscissa = px0
        ordinate = py0 + 20 * y_scale
        base_valuey = ((pyf-py0)/2) / y_scale
        
        while abscissa < pxf:
            w.create_line(abscissa, py0, abscissa, pyf, tag="plot", fill="gray", dash=(1,5))
            w.create_line(abscissa, py0 + (pyf-py0)/2 + 3, abscissa, py0 + (pyf-py0)/2 - 3, tag="plot")
            x_value = int((abscissa-px0) / x_scale)
            w.create_text(abscissa+3, py0 + (pyf-py0)/2 + 8, text="{}".format(x_value), tag="plot", font=("Courier", 6))
            w.create_text(pxf-25, py0 + (pyf-py0)/2 + 15, text="t [s]", tag="plot", font=("Courier", 8))
            
            abscissa += x_scale
       
        while ordinate < pyf:
            w.create_line(px0, ordinate, pxf, ordinate, tag="plot", fill="gray", dash=(1,5))
            w.create_line(px0, ordinate, px0 + 6, ordinate, tag="plot")
            y_value = - (((ordinate - py0) / y_scale) - base_valuey)
            if y_value != 0.0:
                w.create_text(px0 + 20, ordinate, text="{}".format(y_value), tag="plot", font=("Courier", 6))
            ordinate += 20 * y_scale
    else:
        if len(simulation_states) > 1:
            speedm2 = (simulation_states[-2]['vy']**2 + simulation_states[-2]['vx']**2)**0.5
            speedm1 = (simulation_states[-1]['vy']**2 + simulation_states[-2]['vx']**2)**0.5
            
            w.create_line(px0 + simulation_states[-2]['t']*x_scale, py0 + (pyf-py0)/2 + simulation_states[-2]['vy']*y_scale,\
                          px0 + simulation_states[-1]['t']*x_scale, py0 + (pyf-py0)/2 + simulation_states[-1]['vy']*y_scale,\
                          fill=vycol, tag="state")
           
            w.create_line(px0 + simulation_states[-2]['t']*x_scale, py0 + (pyf-py0)/2 - simulation_states[-2]['vx']*y_scale,\
                         px0 + simulation_states[-1]['t']*x_scale, py0 + (pyf-py0)/2 - simulation_states[-1]['vx']*y_scale,\
                         fill=vxcol, tag="state")
                         
            w.create_line(px0 + simulation_states[-2]['t']*x_scale, py0 + (pyf-py0)/2 - simulation_states[-2]['loss']/100*y_scale,\
                                 px0 + simulation_states[-1]['t']*x_scale, py0 + (pyf-py0)/2 - simulation_states[-1]['loss']/100*y_scale,\
                                 fill=wcol, tag="state")
                                 
            w.create_line(px0 + simulation_states[-2]['t']*x_scale, py0 + (pyf-py0)/2 - speedm2*y_scale,\
                                 px0 + simulation_states[-1]['t']*x_scale, py0 + (pyf-py0)/2 -speedm1*y_scale,\
                                 fill=vmcol, tag="state")

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

dumped = ttk.Checkbutton(master, text="Dumped", command=dumpswitched).place(x=800,y=30)
bField = ttk.Entry(master)
bField.insert(0,"{}".format(b_air))
bField.place(x=900, y=30)
bField.state(['disabled'])
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
callback_args.append(bField)

w.place(x=10, y=80)
master.bind("<Return>", keydown)
w.bind("<B1-Motion>", mousemotion)
w.bind("<ButtonRelease-1>", mouserelease)
w.bind("<Button-4>", mousewheelup)
w.bind("<Button-5>", mousewheeldown)


initprojectile(0, 0)
w.create_text(wwidth-100, 60, tag="timetext", text="t = 0.00000 s", font=("Courier", 10))
master.mainloop()
