import tkinter
import time
import socket
import sys
import selectors
import types
import random
import math
 
def serviceConnection(key, mask):
  sock = key.fileobj
  data = key.data
  if mask & selectors.EVENT_READ:
    recv_data = sock.recv(1024)  # Should be ready to read
    if recv_data:
      data.outb = recv_data
      #print(f"Command {data.outb!r} from {data.addr}")
      cms = data.outb.decode("utf-8")
      cmds = cms.split(";")
      botIndex = int(cmds[0]) - 1
      botCmd = cmds[1]
      if botCmd == "scan":
        #print("Scan commd: ", cms)
        botParm1 = cmds[2]
        botParm2 = cmds[3]
        robots[botIndex].myScan(int(botParm1),int(botParm2))
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
      if botCmd == "setDirection":
        botParm1 = cmds[2]
        robots[botIndex].setSpeedGoal(int(botParm1))
        #reply = "%d;%d" % (robots[botIndex].x, 4)
        data.outb = ""
        recv_data = ""
        return
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
class myCanvas(tkinter.Canvas):

  def __init__(self, window, height, width):
    super().__init__(window, height=f'{height}', width=f'{width}')
    self.height = height
    self.width = width
    self.xscale = width/1000
    self.yscale = height/1000

  def makeBot(self, x, y, color):
    x = x * self.xscale
    y = self.height - y * self.yscale
    return super(myCanvas, self).create_polygon(x-3,y-3, x-3,y+3, x+3,y+3, x+3,y-3, fill=color, outline="Black", width=1)

  # Move thing by x and y increments
  def move(self,thing,x,y):
    x = x * self.xscale
    y = y * self.yscale    
    super(myCanvas, self).move(thing,x,y*-1)

# Window that frames the arena canvas
def createFrame(width, height):
  Window = tkinter.Tk()
  Window.title("Arena")
  Window.geometry(f'{width}x{height}')
  return Window

# Arena canvas 
def createArena(window, height, width):
  canvas = myCanvas(window, height, width)
  canvas.configure(bg="Green")
  canvas.pack(expand=False)
  return canvas

def main():
  # Create frame and arena - same size
  frame = createFrame(500,500)
  arena = createArena(frame, 500, 500)

  bot = arena.makeBot(750, 250, "lightgreen")

  startTime = time.time()

  HOST = "127.0.0.1"               # Symbolic name meaning all available interfaces
  PORT = 50007              # Arbitrary non-privileged port

  lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  lsock.bind((HOST, PORT))
  lsock.listen()
  print(f"Listening on {(HOST, PORT)}")
  lsock.setblocking(False)
  sel.register(lsock, selectors.EVENT_READ, data=None)

  try:
    while True:
      # don't block
      events = sel.select(timeout=-10)
      for key, mask in events:
        # listening socket
        if key.data is None:
          accept_wrapper(key.fileobj)
        else:
          serviceConnection(key, mask)
      for r in bots():
        r.update()
      for s in shells():
        s.update()
      arena.move(bot,0,1)
      frame.update()
      time.sleep(.033)
  except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
  finally:
    sel.close()
    sys.exit()

main()

