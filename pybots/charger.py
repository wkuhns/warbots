
import userRobot
import random
import time

mybot = userRobot.mybot

mybot.heading = 0
mybot.myspeed = 35
mybot.scanDirection = 0
mybot.runTimer = 0
mybot.hunting = False
mybot.shells = 4
mybot.resolution = 10
mybot.shotWaiting = False
mybot.shotTimer = time.time()
mybot.reloadWaiting = False
mybot.reloadTimer = time.time()

mybot.closestDist = 2000
mybot.closestHeading = 0

mybot.scanStart = 0
mybot.scanEnd = 359
mybot.huntStart = 0
mybot.huntEnd = 10

mybot.bheat = 0

def setup():
  mybot.set_name("Charger")
  mybot.drive(mybot.heading,mybot.myspeed)

def ping(enemy):
  mybot.myspeed = 100
  mybot.drive(mybot.myspeed, mybot.heading)
  mybot.runTimer = time.time() + 3

def move():

  # See if we need to turn
  olddir = mybot.heading
  if (mybot.x() > 950 and (mybot.heading > 270 or mybot.heading < 90)):
    mybot.heading = 90
    mybot.scanStart = 90
    mybot.scanEnd = 270

  if (mybot.x() < 50 and (mybot.heading < 270 and mybot.heading > 90)):
    mybot.heading = 270
    mybot.scanStart = 270
    mybot.scanEnd = 90

  if (mybot.y() > 950 and (mybot.heading > 0 and mybot.heading < 180)):
    mybot.heading = 180
    mybot.scanStart = 180
    mybot.scanEnd = 359

  if (mybot.y() < 50 and (mybot.heading > 180 and mybot.heading < 360)):
    mybot.heading = 0
    mybot.scanStart = 0
    mybot.scanEnd = 180

  # If we're turning, set new scandir and slow down
  if mybot.heading != olddir:
    mybot.drive(20, mybot.heading)
    # If we're not hunting, reset search
    if mybot.hunting == False:
      mybot.scanDirection = mybot.heading

  # If we're not turning, go normal speed
  else:
    if (time.time() > mybot.runTimer):
      mybot.myspeed = 35
    mybot.drive(mybot.myspeed, mybot.heading)

  # Check timers
  if time.time() > mybot.shotTimer:
    mybot.shotWaiting = False
  if time.time() > mybot.reloadTimer and mybot.reloadWaiting == True:
    mybot.reloadWaiting = False
    # Start looking for closest enemy
    mybot.scanDirection = (mybot.closestHeading + 340) % 360

  # If we're reloading do a full scan
  if mybot.reloadWaiting == True:
    result = int(mybot.scan(mybot.scanDirection, 10))
    if result > 0:
      if result < mybot.closestDist:
        mybot.closestDist = result
        mybot.closestHeading = mybot.scanDirection
    mybot.scanDirection = (mybot.scanDirection + 10) % 360
    if mybot.scanDirection == mybot.scanEnd:
      mybot.scanDirection = mybot.scanStart

  # Not reloading, so just looking for next victim
  if mybot.hunting == False and mybot.reloadWaiting == False:
    result = int(mybot.scan(mybot.scanDirection, mybot.resolution))
    if (result > 40 and result <= 200 and mybot.shotWaiting == False and mybot.reloadWaiting == False):
      mybot.post("Firing close")
      mybot.fire(mybot.scanDirection, result)
    if (result > 200 and result < 600):
      mybot.hunting = True
      mybot.post("Hunting")
      mybot.huntStart = (mybot.scanDirection + 355) % 360
      mybot.huntEnd = (mybot.scanDirection + 5) % 360
      mybot.scanDirection = mybot.huntStart
      mybot.resolution = 3
    else:
      mybot.scanDirection = (mybot.scanDirection + mybot.resolution) % 360

  if mybot.hunting == True:
    result = int(mybot.scan(mybot.scanDirection, mybot.resolution))
    # Fire if we can
    if (result > 40 and result < 690 and mybot.shotWaiting == False and mybot.reloadWaiting == False):
      postmsg = f'Firing in hunt {mybot.resolution}'
      mybot.post(postmsg)
      mybot.fire(mybot.scanDirection, result)
      mybot.shells -= 1
      mybot.shotTimer = time.time() + 4
      mybot.shotWaiting = True
      # If we have to reload, we'll do a full scan and find everyone
      if mybot.shells <= 0:
        mybot.post("Reloading")
        mybot.reloadTimer = time.time() + 12
        mybot.shells = 4
        mybot.hunting == False
        mybot.reloadWaiting = True
        mybot.scanDirection = mybot.scanStart
        mybot.closestDist = 2000
        mybot.resolution = 10
      mybot.scanDirection = (mybot.scanDirection + 340) % 360
      mybot.scanEnd = (mybot.scanDirection + 20) % 360

    else:
      mybot.scanDirection = (mybot.scanDirection + mybot.resolution) % 360
      if mybot.scanDirection > mybot.huntEnd:
        mybot.post("Lost our target")
        mybot.resolution = 10
        mybot.hunting = False

  if mybot.heading == 0:
    # Heading east: scan 0 to 180
    if mybot.scanDirection > 180:
      mybot.scanDirection = 0

  if mybot.heading == 90:
    # Heading north: scan 90 to 270
    if mybot.scanDirection < 90 or mybot.scanDirection > 270:
      mybot.scanDirection = 90

  if mybot.heading == 180:
    # Heading west: scan 180 to 360
    if mybot.scanDirection < 180:
      mybot.scanDirection = 180

  if mybot.heading == 270:
    # Heading south: scan 270 to 90
    if mybot.scanDirection < 270 and mybot.scanDirection > 90:
      mybot.scanDirection = 270


# Do not change these lines
mybot.move = move
mybot.ping = ping
mybot.setup = setup
mybot.main()

