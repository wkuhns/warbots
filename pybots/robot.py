import random
import math
import time

QUANTA = 30
colors = ["dodger blue", "lightgreen", "red", "yellow"]

# Code for robot instance on server
class serverRobot():
  lastReport = 0
  braking = False
  coasting = False

  # for transient graphics
  scanLine1 = 0
  scanLine2 = 0
  scantime = 0
  bombIcon = 0
  bombTime = 0

  # for loading shells
  loadingFinishTime = 0
  loading = False
  shells = 4

  def __init__(self, index, arena, robots):
    self.index = index
    self.arena = arena
    self.robots = robots
    self.used = 0
    self.name = "Robot"
    self.deltax = 0
    self.deltay = 0
    self.status = "D"
    self.color = 0
    self.pingnotify = 0   # ID of bot who scanned me

    self.dir = 45
    self.dirgoal = 45
    self.dirdelta = 0    # +/- increment to turn
    self.currentSpeedMPS = 1       # current speed in meters/sec
    self.speedGoalMPS = 0   # requested speed in meters/sec
    self.shells = 4
    self.mHeat = 0       # motor heat
    self.bHeat = 0       # barrel heat
    self.tx = 0          # target x,y
    self.ty = 0
    #self.scan = 0       # scanning flag - at present,
                          # set by scan method and cleared
                          # when display accesses scan data
    self.sdir = 45
    self.sres = 10
    self.lastscanned = 0  # ID of last 'bot who I scanned
    self.health = 100
    self.maxSpeedMPS = 20

    # Shell variables
    self.ticks = 0

  def time():
    return self.arena.time()

  def sendMessage(self,reply):
    #print("sending: ", reply)
    reply = reply + ':'
    self.sock.send(reply.encode("utf-8"))
    #time.sleep(.001)

  def report(self):
    speed = int(self.currentSpeedMPS*100/self.maxSpeedMPS)
    dir = (360 - self.dir) % 360
    reply = "%d;status;%d;%d;%d;%d;%d;%d;%d" % (self.index,self.x,self.y,self.health,self.mHeat,speed,dir,self.pingnotify)
    self.sendMessage(reply)

  def myFire(self, dir, range):
    # Return with no action if robot is dead or game is paused
    if self.status != "A" or self.arena.status != "R":
      reply = "%d;fire;-1" % (self.index)
      self.sendMessage(reply)
      return

    #print("Firing", dir, range)
    goodToFire = True
    if range < 40:
      goodToFire = False

    if range > 700:
      goodToFire = False

    if dir < 0 or dir > 359:
      goodToFire = False

    if time.time() < self.loadingFinishTime:
      goodToFire = False

    if goodToFire == True:
      if (self.scanLine1 != 0):
        self.arena.delete(self.scanLine1)
        self.arena.delete(self.scanLine2)
        self.scanLine1 = 0
      if (self.bombIcon != 0):
        self.arena.delete(self.bombIcon)
        
      dist = range
      rtheta = dir / 57.3
      self.xt = self.x + dist * math.cos(rtheta)
      self.yt = self.y + dist * math.sin(rtheta)
      self.tick1 = self.arena.line(self.xt-10, self.yt, self.xt+10, self.yt, fill=colors[self.index-1])
      self.tick2 = self.arena.line(self.xt, self.yt-10, self.xt, self.yt+10, fill=colors[self.index-1])
      self.startx = self.x
      self.starty = self.y
      self.ticks = dist / 200 * QUANTA
      self.tickCount = self.ticks
      self.shelldx = dist * math.cos(rtheta) / self.ticks
      self.shelldy = dist * math.sin(rtheta) / self.ticks
      self.ticks = int(self.ticks)
      self.shellIcon = self.arena.circle(self.x, self.y, 4, fill=colors[self.index-1])

      self.bHeat += 20
      self.shells -= 1
      self.loadingFinishTime = time.time() + 4
      self.loading = True
      print("Shells left", self.index, self.shells)
      if self.shells == 0:
        print("Reloading", self.index)
        self.loadingFinishTime += 8
        self.shells = 4
      reply = "%d;fire;0" % (self.index)
    else:
      print ("Misfire", self.index)
      reply = "%d;fire;-1" % (self.index)
    self.sendMessage(reply)

  def place(self,sock, x, y):
    
    self.botIcon = self.arena.makeBot(x, y, colors[self.index-1])
    #self.x = self.rect.centerx
    #self.y = 999 - self.rect.centery
    self.sock = sock
    self.name = "Temp"
    self.used = 1
    #self.quadrant = q
    self.x = x
    self.y = y
    self.currentSpeedMPS = 0
    self.speedGoalMPS = 0
    self.dir = random.randint(0,359)
    self.deltax = 0
    self.deltay = 0
    self.dirgoal = self.dir
    self.dirdelta = 0
    self.health = 100
    self.shells = 4
    self.status = "A"
    self.mHeat = 50
    self.bHeat = 0
    self.reload = 0
    self.fire = 0
    self.cooling = False
    #self.scan = 0
    #blitRotateCenter(arena, self.image, self.x, angle):
    self.lastReport = time.time()
    print (f"Placed x {self.x} y {self.y}")
    reply = "0;place;%d;%d;%d;%d" % (self.index,self.x,self.y,self.dir)
    #print(reply)
    self.sendMessage(reply)

    return self.index

  # set direction and speed
  def drive(self, direction, speed):
    # Return with no action if robot is dead or game is paused
    if self.status != "A" or self.arena.status != "R":
      return

    #print (f"Processing {direction} {speed}")
    speed = max(speed,0)
    speed = min(speed,100)
    # commanded speed in m/sec
    speed = speed / 100 * self.maxSpeedMPS

    if (self.currentSpeedMPS == 0):
      self.coasting = False

    # Are we coasting? do nothing until stopped
    if self.coasting:
      return

    # Are we braking? Don't change speed goal
    if (self.braking and self.currentSpeedMPS <= self.speedGoalMPS):
      self.braking = False

    if (not self.braking):
      self.speedGoalMPS = speed

    #self.dirgoal = (360-direction) % 360
    self.dirgoal = direction
    delta = self.dirgoal - self.dir

    if delta > 180:
      delta = delta - 360
    if delta <= -180:
      delta = delta + 360

    # Is commanded speed too fast? Coast to stop in current dir.
    if abs(delta) > 75 and speed > 4 and self.currentSpeedMPS > 4:
        self.coasting = True
    if abs(delta) > 50 and speed > 7.5 and self.currentSpeedMPS > 7.5:
        self.coasting = True
    if abs(delta) > 25 and speed > 10 and self.currentSpeedMPS > 10:
        self.coasting = True

    # is current speed too fast?
    if abs(delta) > 75 and self.currentSpeedMPS > 4:
        self.braking = True
        self.speedGoalMPS = 4
    if abs(delta) > 50 and self.currentSpeedMPS > 7.5:
        self.braking = True
        self.speedGoalMPS = 7.5
    if abs(delta) > 25 and self.currentSpeedMPS > 10:
        self.braking = True
        self.speedGoalMPS = 10

    if self.coasting:
      delta = 0
      self.speedGoalMPS = 0
      self.dirgoal = self.dir

    self.dirdelta = delta
    #print (f"Speed goal = {self.speedGoalMPS}, dirgoal = {self.dirgoal}")

  def update(self):
    #print("bot update")
    if self.used == 0 or self.status == "D" or self.arena.status != "R":
      return
    
    self.shellUpdate()

    if ((self.scantime + 0.1) < time.time()) and (self.scanLine1 != 0):
    #if self.scanLine1 != 0:
      self.arena.delete(self.scanLine1)
      self.arena.delete(self.scanLine2)
      self.scanLine1 = 0
    if time.time() > self.bombTime and self.bombIcon != 0:
      self.arena.delete(self.bombIcon)
      #print("erase")
    # adjust heading if we're turning
    if self.dirdelta != 0:
      # calculate turning rate
      newrate = int(self.currentSpeedMPS / 25)
      if newrate == 4: 
          rate = 30 / QUANTA
      elif newrate == 3: 
          rate = 30 / QUANTA
      elif newrate == 2: 
          rate = 40 / QUANTA
      elif newrate == 1: 
          rate = 60 / QUANTA
      elif newrate == 0: 
          rate = 90 / QUANTA
      
      delta = self.dirdelta
      if (delta > rate):
        delta = rate
      if (delta < rate * -1):
        delta = rate * -1
      self.dir = (self.dir + delta) % 360
      #print("dir: ", self.dir)
      self.dirdelta = self.dirdelta - delta
      self.deltax = self.currentSpeedMPS * math.cos(self.dir / 57.3) / QUANTA
      self.deltay = self.currentSpeedMPS * math.sin(self.dir / 57.3) / QUANTA

    # barrel cooling
    self.bHeat = self.bHeat - (2 / QUANTA)

    if self.bHeat < 0:
      self.bHeat = 0

    # motor heating
    speedPct = self.currentSpeedMPS * 100 / self.maxSpeedMPS
    # heating is 4 degrees per second at 35%, 8 degree per second at 70%, 12 at 105%
    # cooling is 2 degrees per second at 100 deg, 4 at 200
    # equilibrium is 100 deg at 35%, 200 deg at 70% 300 at 105%
    heat = speedPct * 5 / 35 - 3
    heat = max(heat,0)
    cool = self.mHeat * 3 / 100
    #print("temp %0.0f speedPct %0.0f heat %0.0f cool %0.0f" % (self.mHeat, speedPct, heat, cool))
    self.mHeat = self.mHeat + (heat - cool) / QUANTA

    if self.mHeat >= 200:
      self.cooling = True
      self.mHeat = 200
    
    # Check if we overheated and are cooling
    if self.cooling:
      self.currentSpeedMPS = min(self.maxSpeedMPS * .35, self.currentSpeedMPS)
      self.speedGoalMPS = min(self.maxSpeedMPS * .35, self.speedGoalMPS)
      self.deltax = self.currentSpeedMPS * math.cos(self.dir / 57.3) / QUANTA
      self.deltay = self.currentSpeedMPS * math.sin(self.dir / 57.3) / QUANTA
      if self.mHeat <= 180:
        self.cooling = False

    if self.mHeat < 0:
      self.mHeat = 0

    # adjust speed
    delta = self.speedGoalMPS - self.currentSpeedMPS
    if delta != 0:
      if (delta > (10 / QUANTA)):
        delta = (10 / QUANTA)
      if (delta < (-10 / QUANTA)):
        delta = (-10 / QUANTA)
      self.currentSpeedMPS = self.currentSpeedMPS + delta
      # calculate per tick movement
      self.deltax = self.currentSpeedMPS * math.cos(self.dir / 57.3) / QUANTA
      self.deltay = self.currentSpeedMPS * math.sin(self.dir / 57.3) / QUANTA
      #print("Speed: ", self.currentSpeedMPS, "Direction: ", self.dir, "Coasting: ", self.coasting, "Braking: ", self.braking)

    # Move the puppy
    newx = self.x + self.deltax
    if newx > 999 or newx < 0:
      self.currentSpeedMPS = 0
      self.speedGoalMPS = 0
      self.deltax = 0
      self.deltay = 0
      #Call wound(i, 5)
    else:
      self.x = newx
    
    # y is upside down - 0 at top
    newy = self.y + self.deltay
    if newy > 999 or newy < 0:
      self.currentSpeedMPS = 0
      self.speedGoalMPS = 0
      self.deltax = 0
      self.deltay = 0
      #Call wound(i, 5)
    else:
        self.y = newy
    #print(self.deltax, self.deltay)
    self.arena.move(self.botIcon, self.deltax, self.deltay)

    if self.reload > 0:
      self.reload = self.reload - 1 / QUANTA

    if((time.time() - self.lastReport) > .5):
      #print ("Setting...")
      self.lastReport = time.time()
      #print("Reporting...")
      self.panel.setSpeed(self.currentSpeedMPS)
      self.panel.setMheat(self.mHeat)
      self.panel.setDir(self.dir)
      self.panel.setBheat(self.bHeat)
      self.report()
      #print("scanning")
      #self.myScan()

  def shellUpdate(self):
    if self.ticks == 0:
      return
    self.ticks += -1
    if self.ticks <= 0:
      self.ticks = 0;
      self.explode()
      return
    coords = self.arena.center(self.shellIcon)
    self.shellx = coords[0]
    self.shelly = coords[1]

    dx = (self.startx + (self.shelldx * int(self.tickCount - self.ticks))) - self.shellx
    dy = (self.starty + (self.shelldy * int(self.tickCount - self.ticks))) - self.shelly
    self.arena.move(self.shellIcon, dx, dy)    

  def explode(self):
    self.arena.delete(self.tick1)
    self.arena.delete(self.tick2)
    self.arena.delete(self.shellIcon)
    self.bombIcon = self.arena.circle(self.xt, self.yt, 40, fill="red")
    self.bombTime = time.time() + .1

    for r in self.robots:
      #print("Checking", r.index)
      dist = math.sqrt((self.xt - r.x)**2 + (self.yt - r.y)**2)
      #print (dist)
      damage = 0
      if dist < 40:
        damage = 3
      if dist < 20:
        damage = 7
      if dist < 10:
        damage = 12
      if dist < 6:
        damage = 25
      if damage > 0:
        print("wounding")
        r.wound(damage)
    #print ("done exploding")

  def scan(self, dir, res):
    # Return with no action if robot is dead or game is paused
    if self.status != "A" or self.arena.status != "R":
      reply = "%d;scan;0;0" % (self.index)
      self.sendMessage(reply)
      return

    self.sdir = dir
    self.sres = res
    theta1 = (self.sdir - self.sres/2)
    if theta1 < 0:
      theta1 += 360
    theta2 = (self.sdir + self.sres/2)
    endx = (1500 * math.cos(theta1 / 57.3)) + self.x
    endy = (1500 * math.sin(theta1 / 57.3)) + self.y
    #print("bot:", int(self.x), int(self.y), int(endx), int(endy))
    #print(self.x, self.y, endx, endy) 
    #pygame.draw.line(self.arena, (0, 0, 0), (self.x,1000-self.y), (endx,1000-endy))
    self.scanLine1 = self.arena.line(self.x, self.y, endx, endy, fill=colors[self.index-1])
    #print (type(self.scanLine1))
    endx = (1500 * math.cos(theta2 / 57.3)) + self.x
    endy = (1500 * math.sin(theta2 / 57.3)) + self.y  
    #pygame.draw.line(self.arena, (0, 0, 0), (self.x,1000-self.y), (endx,1000-endy))
    self.scanLine2 = self.arena.line(self.x, self.y, endx, endy, fill=colors[self.index-1])
    self.scantime = time.time()
    # See if we saw anyone

    dist = 2000
    closest = 0
    for r in self.robots:

      if r.status == "A" and r.index != self.index:

        rtheta = math.atan2((r.y - self.y), (r.x - self.x))

        if rtheta < 0:
          rtheta += (2 * math.pi)
        rtheta = rtheta * 57.3

        if rtheta > theta1 and rtheta < theta2:
          myDist = math.sqrt((r.y - self.y)**2 + (r.x - self.x)**2)
          if myDist < dist:
            dist = myDist
            closest = r.index
          reply = "%d;ping;%d" % (r.index, self.index)
          self.robots[r.index-1].sock.send(reply.encode("utf-8"))

    if dist == 2000:
      dist = 0

    # Add in errors: error based on scan width
    if self.bHeat > 35:
      dist = 0
      closest = 0

    if dist > 0:
      dist += random.randint(-1 * self.sres, self.sres)
      #print (dist)
      # Barrel heat
      if random.randint(0,1):
        dist += self.bHeat
      else:
        dist -= self.bHeat

    #print("Dist, bheat", dist, self.bHeat)

    reply = "%d;scan;%d;%d" % (self.index, dist, closest)
    self.sendMessage(reply)

  def wound(self, damage):
    self.health -= damage
    print (f"Robot {self.index-1} health: {self.health}")
    self.panel.setHealth(self.health)
    if self.health <= 0:
      print ("Robot dead: ", self.index-1)
      self.speedGoalMPS = 0
      self.currentSpeedMPS = 0
      self.status = "D"

