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

class Bot():
  index = -1
  __xcoordinate = -1
  __ycoordinate = -1
  myhealth = -1
  __myheat = -1
  __myspeed = -1
  __mydirection = -1
  __mydsp = -1

  __scanResponse = 0
  __sock = ""
  __sleepUntil = time.time()
  __name = "unnamed"
  __data = []

  def __init__(self):
    self.mydirection = -1
    self.sleepUntil = time.time()
    # start_connections returns the socket that we'll need.
    # Establish communications, then place the robot
    self.sock = self.start_connections(HOST, int(PORT), 1)
    reply = "0;place"
    self.send_message(reply)
 
  def setup(self):
    print("Empty setup function")

  def x(self):
    return self.xcoordinate

  def y(self):
    return self.ycoordinate

  def health(self):
    return self.myhealth

  def heat(self):
    return self.myheat

  def speed(self):
    return self.myspeed

  def direction(self):
    return self.mydirection

  def dsp(self):
    return self.mydsp

  def ping(self, enemy):
    print ("Empty ping function")

  def move(self):
    print("Empty move function")
  
  def place(self, sock):
    self.sock = sock
    reply = "0;place"
    self.send_message(reply)

  def set_name(self,name):
    self.name = name
    reply = "%d;set_name;%s;" % (self.index, name)
    self.send_message(reply)

  def set_armor(self,lvl):
    lvl = min(lvl, 100)
    lvl = max(lvl, 0)
    reply = "%d;setArmor;%d;" % (self.index, lvl)
    self.send_message(reply)
    
  def set_scan(self,lvl):
    lvl = min(lvl, 100)
    lvl = max(lvl, 0)
    reply = "%d;setScan;%d;" % (self.index, lvl)
    self.send_message(reply)
    
  # Don't return until time has passed
  def check_sleep(self):
    while time.time() < self.sleepUntil:
      events = sel.select(timeout=-10)
      for key, mask in events:
        self.service_connection(key, mask)
      time.sleep(.01)

  def send_message(self,reply):
    #print("sending: ", reply)
    reply = reply + '|'
    self.sock.send(reply.encode("utf-8"))

  def scan(self, direction, res):

    self.scanResponse = -1
    reply = "%d;scan;%d;%d" % (self.index, direction, res)
    #print("Scanning: ", reply)
    self.send_message(reply)
    self.sleepUntil = time.time() + .2
    self.check_sleep()
    return self.scanResponse

  def drive(self, speed, direction):
    #print("Dir",direction, "speed",speed)
    if self.index != -1:
      reply = "%d;drive;%d;%d" % (self.index, direction, speed)
      self.send_message(reply)
      self.sleepUntil = time.time() + .1
      self.check_sleep()

  def post(self, msg):
    reply = "%d;post;%s" % (self.index, msg)
    self.send_message(reply)

  def fire(self, direction, range):
    self.check_sleep()
    reply = "%d;fire;%d;%d" % (self.index, direction, range)
    self.send_message(reply)
    self.sleepUntil = time.time() + .1
    self.check_sleep()
    
  def process_response(self, response):
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
        self.xcoordinate = int(rs[3])
        self.ycoordinate = int(rs[4])
        self.mydirection = int(rs[5])
        self.setup()
        print(f"We are robot {self.index }")
        return
      if rs[1] == "scan":
        self.scanResponse = int(rs[2])
        self.mydsp = int(rs[3])
        #break
      if rs[1] == "fire":
        if rs[2] != "0":
          self.sleepUntil += .1
        #break
      if rs[1] == "status":
        self.xcoordinate = int(rs[2])
        self.ycoordinate = int(rs[3])
        self.myhealth = int(rs[4])
        self.myheat = int(rs[5])
        self.myspeed = int(rs[6])
        self.mydirection = int(rs[7])
        self.mydsp = int(rs[8])
        #print(f"xcoordinate={self.x} y={self.y} dir={self.dir} speed={self.speed}")
        #break
      #error if not ours
      if int(rs[0]) != self.index:
        print(f"Wrong client: {r}")
        #break
      if rs[1] == "ping":
        self.ping(int(rs[2]))
        #print(msg, rs[2], int(rs[2]))
        #break

  def start_connections(self, HOST, PORT, num_conns):
    #global mybot
    server_addr = (HOST, PORT)
    connid=0
    print(f"Starting connection to {server_addr}... ", end = '')
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
        self.process_response(recv_data)
      if not recv_data or data.recv_total == data.msg_total:
        print(f"Closing connection {data.connid}")
        sel.unregister(sock)
        sock.close()
      recv_data = ""

  def set_autopilot(self):
    reply = "%d;set_autopilot" % (self.index)
    self.send_message(reply)
    print(reply)
    
  def set_autoscan(self):
    reply = "%d;set_autoscan" % (self.index)
    self.send_message(reply)
    
  def main(self):
    
    #try:
    while True:
      while time.time() < self.sleepUntil:
        events = sel.select(timeout=-10)
        for key, mask in events:
          self.service_connection(key, mask)
        time.sleep(.01)
      if(self.myhealth > 0):
        self.move()

      # If user didn't do something that takes time, wait 50 msec
      if time.time() >= self.sleepUntil:
        self.sleepUntil = time.time() + .05
    #except KeyboardInterrupt:
    #  print("Caught keyboard interrupt, exiting")
    #finally:
    #  sel.close()
    #  sys.exit()

mybot = Bot()
