import socket
import sys
import selectors
import types
import time
#import math
#import random

HOST = 'localhost'    # The remote host
PORT = 50007          # The same port as used by the server
QUANTA = 10           # frames per second

sel = selectors.DefaultSelector()
messages = [b""]

class bot():
  index = -1
  x = -1
  y = -1
  health = -1
  heat = -1
  speed = -1
  direction = -1
  dsp = -1

  scanResponse = 0
  sock = ""
  sleepUntil = time.time()
  name = "unnamed"
  data = []

  def __init__(self):
    print("init")
    self.direction = -1
    self.sleepUntil = time.time()
    # start_connections returns the socket that we'll need.
    # Establish communications, then place the robot
    self.sock = self.start_connections(HOST, int(PORT), 1)
    reply = "0;place"
    self.sendMessage(reply)
 
  def setup(self):
    print("Empty setup function")

  def ping(self, enemy):
    print ("Empty ping function")

  def move(self):
    print("Empty move function")
  
  def place(self, sock):
    self.sock = sock
    reply = "0;place"
    self.sendMessage(reply)

  def setName(self,name):
    self.name = name
    reply = "%d;setName;%s;" % (self.index, name)
    self.sendMessage(reply)

  # Don't return until time has passed
  def checkSleep(self):
    while time.time() < self.sleepUntil:
      events = sel.select(timeout=-10)
      for key, mask in events:
        self.service_connection(key, mask)
      time.sleep(.01)

  def sendMessage(self,reply):
    #print("sending: ", reply)
    self.sock.send(reply.encode("utf-8"))

  def scan(self, direction, res):

    self.scanResponse = -1
    reply = "%d;scan;%d;%d" % (self.index, direction, res)
    #print("Scanning: ", reply)
    self.sendMessage(reply)
    self.sleepUntil = time.time() + .2
    self.checkSleep()
    return self.scanResponse

  def drive(self, direction, speed):
    #print("Dir",direction, "speed",speed)
    if self.index != -1:
      reply = "%d;drive;%d;%d" % (self.index, direction, speed)
      self.sendMessage(reply)
      self.sleepUntil = time.time() + .1
      self.checkSleep()

  def fire(self, direction, range):
    self.checkSleep()
    reply = "%d;fire;%d;%d" % (self.index, direction, range)
    self.sendMessage(reply)
    self.sleepUntil = time.time() + .1
    self.checkSleep()
    
  def processResponse(self, response):
    r = response.decode("utf-8")
    #print("Messages: ", r)
    msgs = r.split(':')
    for msg in msgs:
      if msg == "":
        return
      rs = msg.split(";")
      #print(f"Processing {msg}")
      # 'place' response: 0;place;index
      if rs[1] == "place":
        self.index = int(rs[2])
        self.x = int(rs[3])
        self.y = int(rs[4])
        self.direction = int(rs[5])
        self.setup()
        print(f"We are # {self.index }")
        return
      if rs[1] == "scan":
        self.scanResponse = int(rs[2])
        self.dsp = int(rs[3])
        #break
      if rs[1] == "fire":
        if rs[2] != "0":
          self.sleepUntil += .1
        #break
      if rs[1] == "status":
        self.x = int(rs[2])
        self.y = int(rs[3])
        self.health = int(rs[4])
        self.heat = int(rs[5])
        self.speed = int(rs[6])
        self.direction = int(rs[7])
        self.dsp = int(rs[8])
        #print(f"x={self.x} y={self.y} dir={self.dir} speed={self.speed}")
        #break
      #error if not ours
      if int(rs[0]) != self.index:
        print(f"Wrong client: {r}")
        #break
      if rs[1] == "ping":
        self.ping(rs[2])
        #break

  def start_connections(self, HOST, PORT, num_conns):
    #global myBot
    server_addr = (HOST, PORT)
    connid=0
    print(f"Starting connection {connid} to {server_addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
      connid=connid,
      msg_total=sum(len(m) for m in messages),
      recv_total=0,
      messages=messages.copy(),
      outb=b""
    )
    sel.register(sock, events, data=data)
    print("Connected")
    return sock

  def service_connection(self, key, mask):

    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
      recv_data = sock.recv(1024)  # Should be ready to read
      if recv_data:
        #print(f"Received {recv_data!r} from connection {data.connid}")
        data.recv_total += len(recv_data)
        self.processResponse(recv_data)
      if not recv_data or data.recv_total == data.msg_total:
        print(f"Closing connection {data.connid}")
        sel.unregister(sock)
        sock.close()
      recv_data = ""

  def main(self):
    
    #try:
    while True:
      while time.time() < self.sleepUntil:
        events = sel.select(timeout=-10)
        for key, mask in events:
          self.service_connection(key, mask)
        time.sleep(.01)
      if(self.health > 0):
        self.move()

      # If user didn't do something that takes time, wait 50 msec
      if time.time() >= self.sleepUntil:
        self.sleepUntil = time.time() + .05
    #except KeyboardInterrupt:
    #  print("Caught keyboard interrupt, exiting")
    #finally:
    #  sel.close()
    #  sys.exit()

myBot = bot()
