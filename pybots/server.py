import time
import socket
import sys
import selectors
import types
import random
import math
import serverRobot
import tkinter as tk
from tkinter import ttk
from tkinter import * 

# this is the function called when the button is clicked
def btnClickFunction():
  print('clicked')

QUANTA = 30
BOTSIZE = 6   
ARENA_SIZE = 800
STATUS_WIDTH = 400
colors = ["dodger blue", "lightgreen", "red", "yellow"]

def serviceConnection(key, mask):
  sock = key.fileobj
  data = key.data
  if mask & selectors.EVENT_READ:
    recv_data = sock.recv(1024)  # Should be ready to read
    if recv_data:
      recv_data = recv_data.decode("utf-8")
      #print(f"Command {data.outb!r} from {data.addr}")
      msgs = recv_data.split("|")
      for msg in msgs:
        if len(msg) < 3:
          break
        cmds = msg.split(";")
        botIndex = int(cmds[0]) - 1
        botCmd = cmds[1]
        if botCmd == "post":
          botParm1 = cmds[2]
          robots[botIndex].post(botParm1)   
        if botCmd == "scan":
          botParm1 = cmds[2]
          botParm2 = cmds[3]
          robots[botIndex].scan(int(botParm1),int(botParm2))
        if botCmd == "place":
          botIndex = placeBot(sock)
          recv_data = ""
          data.outb = ""
          return
        if botCmd == "drive":
          #print(f"Drive #{botIndex}: {cmds[2]} {cmds[3]}")
          botParm1 = cmds[2]
          botParm2 = cmds[3]
          robots[botIndex].drive(int(botParm1),int(botParm2))
          data.outb = ""
          recv_data = ""
          return
        if botCmd == "fire":
          botParm1 = cmds[2]
          botParm2 = cmds[3]
          robots[botIndex].myFire(int(botParm1),int(botParm2))
          data.outb = ""
          recv_data = ""
          return
        if botCmd == "setName":
          robots[botIndex].name = cmds[2]
          print("Calling setname", cmds[2])
          robots[botIndex].panel.setName(cmds[2])
        if botCmd == "setDirection":
          botParm1 = cmds[2]
          robots[botIndex].setSpeedGoal(int(botParm1))
          #reply = "%d;%d" % (robots[botIndex].x, 4)
          data.outb = ""
          recv_data = ""
          return
        if botCmd == "setAutopilot":
          robots[botIndex].autopilot = True
        if botCmd == "setAutoscan":
          robots[botIndex].autoscan = True

    else:
      # Client has closed socket, close our end too
      print(f"Closing connection to {data.addr}")
      sel.unregister(sock)
      sock.close()
    data.outb = ""

def accept_wrapper(sock):
  conn, addr = sock.accept()  # Should be ready to read
  print(f"Accepted connection from {addr}")
  conn.setblocking(False)
  data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  sel.register(conn, events, data=data)

# Subclass of tkinter.Canvas with positive Y axis and arena scaling
class myCanvas(tk.Canvas):

  def __init__(self, window, height, width):
    super().__init__(window, height=f'{height}', width=f'{width}')
    self.height = height
    self.width = width
    self.xscale = width/1000
    self.yscale = height/1000
    self.startTime = time.time()
    self.gameTime = 0
    self.status = "I"         # Initialized, Paused, Running, Finished

  def time():
    return time.time() - self.startTime

  def makeBot(self, x, y, color):
    x = x * self.xscale
    y = self.height - y * self.yscale
    return super(myCanvas, self).create_polygon(x-BOTSIZE,y-BOTSIZE, x-BOTSIZE,y+BOTSIZE, x+BOTSIZE,y+BOTSIZE, x+BOTSIZE,y-BOTSIZE, fill=color, outline="Black", width=1)

  # Move thing by x and y increments
  def move(self,thing,x,y):
    x = x * self.xscale
    y = y * self.yscale    
    super(myCanvas, self).move(thing,x,y*-1)

  def line(self, x1, y1, x2, y2, fill="black"):
    x1 = x1 * self.xscale
    y1 = (1000 - y1) * self.yscale    
    x2 = x2 * self.xscale
    y2 = (1000 - y2) * self.yscale
    return super(myCanvas, self).create_line(x1, y1, x2, y2, fill=f"{fill}")    

  def circle(self, x, y, r, fill=""): #center coordinates, radius
    x0 = (x - r) * self.xscale
    y0 = (1000 - y - r) * self.yscale
    x1 = (x + r) * self.xscale
    y1 = (1000 - y + r) * self.yscale
    return super(myCanvas, self).create_oval(x0, y0, x1, y1, fill=f"{fill}")

  def center(self, cir):
    coords = super(myCanvas, self).coords(cir)
    x = (coords[0] + coords[2]) / 2 / self.xscale
    y = 1000 - ((coords[1] + coords[3]) / 2 / self.yscale)
    return [x, y]

# Window that frames the arena canvas
def createFrame(width, height):
  Window = tk.Tk()
  Window.title("Arena")
  Window.geometry(f'{width}x{height}')
  return Window

# Arena canvas 
def createArena(window, height, width):
  canvas = myCanvas(window, height, width)
  canvas.configure(bg="Green")
  canvas.pack(expand=False)
  return canvas

def placeBot(sock):
  x = 0
  for q in range (0, 3):
    if quads[q].used == 0:
      x = 1
  
  if x == 0:
    print("Quadrant allocation error. Start over.")
    return 0

  # Pick a random quadrant
  q = random.randint(0,3)
  while quads[q].used == 1:
    q = random.randint(0,3)
  print (f"picked {q}")
  quads[q].used = 1
  r = len(robots)
  print(f"placing {r+1}")
  x = random.randint(0,300) + quads[q].x
  y = random.randint(0,300) + quads[q].y

  robots.append(serverRobot.serverRobot(r+1, arena, robots))
  robots[r].place(sock, x, y)
  robots[r].panel = panels[r]
  robots[r].panel.populate(robots[r].name)
  #print(f"Bots: {robots[r].index}")

  print (f"placed {r}")
  return(robots[r].index)

class quad:
  def __init__(self):
    self.used = 0
    self.x = 0
    self.y = 0

quads = [quad(), quad(), quad(), quad()]
quads[0].x = 100
quads[0].y = 100
quads[1].x = 100
quads[1].y = 600
quads[2].x = 600
quads[2].y = 100
quads[3].x = 600
quads[3].y = 600

def makePanel(frame, row):
  recspec = [(2,2), (STATUS_WIDTH - 2, ARENA_SIZE / 5 -2)]
  myPanel = tk.Canvas(frame, width=STATUS_WIDTH, height=ARENA_SIZE / 5 -2, bg="white", bd=1)
  myPanel.grid(column=1, row=row)
  myPanel.create_rectangle(recspec)
  #Label(myPanel, text=title, bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=131, y=3)
  return myPanel

class robotPanel:
  def __init__(self, frame, index):
    self.botPanel = makePanel(frame, index)
    self.index=index
    print("Panel index", index)

  def populate(self, name):
    # Label at top

    # Speed display
    Label(self.botPanel, text='Speed', bg='white', font=('arial', 10, 'normal')).place(x=5, y=10)    
    self.Speed=Entry(self.botPanel)
    self.Speed.config(width=4, justify=RIGHT, font='arial 10')
    self.Speed.place(x=75, y=10)

    # Direction display
    Label(self.botPanel, text='Direction', bg='white', font=('arial', 10, 'normal')).place(x=5, y=40)    
    self.Dir=Entry(self.botPanel)
    self.Dir.config(width=4, justify=RIGHT, font='arial 10')
    self.Dir.place(x=75, y=40)

    # Motor Heat display
    Label(self.botPanel, text='Mtr Heat', bg='white', font=('arial', 10, 'normal')).place(x=5, y=70)    
    self.Mheat=Entry(self.botPanel)
    self.Mheat.config(width=4, justify=RIGHT, font='arial 10')
    self.Mheat.place(x=75, y=70)

    # Barrel Heat display
    Label(self.botPanel, text='Barrel', bg='white', font=('arial', 10, 'normal')).place(x=5, y=100)    
    self.bHeat=Entry(self.botPanel)
    self.bHeat.config(width=4, justify=RIGHT, font='arial 10')
    self.bHeat.place(x=75, y=100)

    # Health status bar
    Label(self.botPanel, text='Health', bg='white', font=('arial', 10, 'normal')).place(x=5, y=130)
    progessBarOne_style = ttk.Style()
    progessBarOne_style.theme_use('clam')
    progessBarOne_style.configure('progessBarOne.Horizontal.TProgressbar', 
      foreground='#FF4040', background='#FF4040')

    self.progessBarOne=ttk.Progressbar(self.botPanel, style='progessBarOne.Horizontal.TProgressbar', 
      orient='horizontal', length=300, mode='determinate', maximum=100, value=100)
    self.progessBarOne.place(x=75, y=130)

    # Message box
    self.msgBox = Text(self.botPanel, height=5, width=38, font=('Arial','10'))
    self.msgBox.place(x=115, y=35)

  def setName(self, name):
    print ("Setting name", name)
    self.nameLabel = Label(self.botPanel, text=name, bg=colors[self.index-1], font=('arial', 12, 'normal')).place(x=151, y=3)
    #self.nameLabel.config(text = name)

  def setHealth(self, val):
    self.progessBarOne['value']=val

  def setMheat(self, val):
    self.Mheat.delete(0,END)
    sval = "%.0f" % val
    self.Mheat.insert(0,sval)
   
  def setSpeed(self, val):
    self.Speed.delete(0,END)
    sval = "%.0f" % val
    self.Speed.insert(0,sval)

  def setDir(self, val):
    self.Dir.delete(0,END)
    sval = "%.0f" % val
    self.Dir.insert(0,sval)

  def setBheat(self, val):
    self.bHeat.delete(0,END)
    sval = "%.0f" % val
    self.bHeat.insert(0,sval)

def startBtnClick():
  if arena.gameTime == 0:
    arena.startTime = time.time()
  arena.status = "R"
  postMessage("Started")

def pauseBtnClick():
  arena.status = "P"
  postMessage("Paused")

def postMessage(msg):
  msg = msg[:50]
  #self.panel.msgBox.insert('1.0', msg + '\n')
  arena.msgBox.insert(END, '\n' + msg)
  arena.msgBox.see(END)

# Create frame and arena - same size
frame = createFrame(ARENA_SIZE + STATUS_WIDTH + 2, ARENA_SIZE + 2)
arena = createArena(frame, ARENA_SIZE, ARENA_SIZE)
arena.grid(column=0, row=0, rowspan=5)

# Status panel Start button
pnlStatus = makePanel(frame, 0)
Button(pnlStatus, text='Start', bg='white', font=('arial', 12, 'normal'), command=startBtnClick).place(x=10, y=10)

# Status panel pause button
Button(pnlStatus, text='Pause', bg='white', font=('arial', 12, 'normal'), command=pauseBtnClick).place(x=90, y=10)

# Status panel game time display
Label(pnlStatus, text='Game Time', bg='white', font=('arial', 10, 'normal')).place(x=250, y=15)    
gTime=Entry(pnlStatus)
gTime.config(width=4, justify=RIGHT, font='arial 10')
gTime.place(x=350, y=20)

# Message box
arena.msgBox = Text(pnlStatus, height=6, width=52, font=('Arial','10'))
arena.msgBox.place(x=10, y=50)

panels = []
for i in range(0,4):
  panels.append(robotPanel(frame, i+1))

sel = selectors.DefaultSelector()
robots = []

def main():

  #bot = arena.makeBot(750, 250, "lightgreen")

  startTime = time.time()

  HOST = "127.0.0.1"               # Symbolic name meaning all available interfaces
  PORT = 50007              # Arbitrary non-privileged port

  lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  lsock.bind((HOST, PORT))
  lsock.listen()
  print(f"Listening on {(HOST, PORT)}")
  lsock.setblocking(False)
  sel.register(lsock, selectors.EVENT_READ, data=None)
  
  #try:
  while True:
    # don't block
    events = sel.select(timeout=-10)
    for key, mask in events:
      # listening socket
      if key.data is None:
        accept_wrapper(key.fileobj)
      else:
        serviceConnection(key, mask)

    # Check if tournament is over
    players = 0
    winner = "none"
    for r in robots:
      if r.status == "A":
        players += 1
        winner = r.name

    # If game is running and 1 or fewer live robots, we're finished.
    if players <= 1 and arena.status == "R":
      arena.status = "F"
      postMessage(f"Finished! The winner is {winner}.")
    else:
      for r in robots:
        r.update()

    if arena.status == "R":
      arena.gameTime = time.time() - arena.startTime
    # If we're paused increment start time
    if arena.status == "P":
      arena.startTime = time.time() - arena.gameTime

    gTime.delete(0,END)
    sval = "%.0f" % arena.gameTime
    gTime.insert(0,sval)
    frame.update()
    time.sleep(.033)

  #except KeyboardInterrupt:
  #  print("Caught keyboard interrupt, exiting")
  #finally:
  #  sel.close()
  #  sys.exit()

main()

