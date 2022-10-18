
import userRobot
import random
import time

myBot = userRobot.myBot

myBot.heading = 0
myBot.mySpeed = 35
myBot.scanDirection = 0
myBot.runTimer = 0
myBot.hunting = False
myBot.shells = 4
myBot.resolution = 10
myBot.shotWaiting = False
myBot.shotTimer = time.time()
myBot.reloadWaiting = False
myBot.reloadTimer = time.time()

myBot.closestDist = 2000
myBot.closestHeading = 0

myBot.scanStart = 0
myBot.scanEnd = 359
myBot.huntStart = 0
myBot.huntEnd = 10

def mySetup():
  myBot.setName("Charger")
  myBot.drive(myBot.heading,myBot.mySpeed)

def myPing(enemy):
  myBot.mySpeed = 100
  myBot.drive(myBot.mySpeed, myBot.heading)
  myBot.runTimer = time.time() + 3

def myMove():

  # See if we need to turn
  olddir = myBot.heading
  if (myBot.x > 950 and (myBot.heading > 270 or myBot.heading < 90)):
    myBot.heading = 90
    myBot.scanStart = 90
    myBot.scanEnd = 270

  if (myBot.x < 50 and (myBot.heading < 270 and myBot.heading > 90)):
    myBot.heading = 270
    myBot.scanStart = 270
    myBot.scanEnd = 90

  if (myBot.y > 950 and (myBot.heading > 0 and myBot.heading < 180)):
    myBot.heading = 180
    myBot.scanStart = 180
    myBot.scanEnd = 359

  if (myBot.y < 50 and (myBot.heading > 180 and myBot.heading < 360)):
    myBot.heading = 0
    myBot.scanStart = 0
    myBot.scanEnd = 180

  # If we're turning, set new scandir and slow down
  if myBot.heading != olddir:
    myBot.drive(20, myBot.heading)
    # If we're not hunting, reset search
    if myBot.hunting == False:
      myBot.scanDirection = myBot.heading

  # If we're not turning, go normal speed
  else:
    if (time.time() > myBot.runTimer):
      myBot.mySpeed = 35
    myBot.drive(myBot.mySpeed, myBot.heading)

  # Check timers
  if time.time() > myBot.shotTimer:
    myBot.shotWaiting = False
  if time.time() > myBot.reloadTimer and myBot.reloadWaiting == True:
    myBot.reloadWaiting = False
    # Start looking for closest enemy
    myBot.scanDirection = (myBot.closestHeading + 340) % 360

  # If we're reloading do a full scan
  if myBot.reloadWaiting == True:
    result = int(myBot.scan(myBot.scanDirection, 10))
    if result > 0:
      if result < myBot.closestDist:
        myBot.closestDist = result
        myBot.closestHeading = myBot.scanDirection
    myBot.scanDirection = (myBot.scanDirection + 10) % 360
    if myBot.scanDirection == myBot.scanEnd:
      myBot.scanDirection = myBot.scanStart

  # Not reloading, so just looking for next victim
  if myBot.hunting == False and myBot.reloadWaiting == False:
    result = int(myBot.scan(myBot.scanDirection, myBot.resolution))
    if (result > 40 and result <= 200 and myBot.shotWaiting == False and myBot.reloadWaiting == False):
      myBot.post("Firing close")
      myBot.fire(myBot.scanDirection, result)
    if (result > 200 and result < 600):
      myBot.hunting = True
      myBot.post("Hunting")
      myBot.huntStart = (myBot.scanDirection + 355) % 360
      myBot.huntEnd = (myBot.scanDirection + 5) % 360
      myBot.scanDirection = myBot.huntStart
      myBot.resolution = 3
    else:
      myBot.scanDirection = (myBot.scanDirection + myBot.resolution) % 360

  if myBot.hunting == True:
    result = int(myBot.scan(myBot.scanDirection, myBot.resolution))
    # Fire if we can
    if (result > 40 and result < 690 and myBot.shotWaiting == False and myBot.reloadWaiting == False):
      postmsg = f'Firing in hunt {myBot.resolution}'
      myBot.post(postmsg)
      myBot.fire(myBot.scanDirection, result)
      myBot.shells -= 1
      myBot.shotTimer = time.time() + 4
      myBot.shotWaiting = True
      # If we have to reload, we'll do a full scan and find everyone
      if myBot.shells <= 0:
        myBot.post("Reloading")
        myBot.reloadTimer = time.time() + 12
        myBot.shells = 4
        myBot.hunting == False
        myBot.reloadWaiting = True
        myBot.scanDirection = myBot.scanStart
        myBot.closestDist = 2000
        myBot.resolution = 10
      myBot.scanDirection = (myBot.scanDirection + 340) % 360
      myBot.scanEnd = (myBot.scanDirection + 20) % 360

    else:
      myBot.scanDirection = (myBot.scanDirection + myBot.resolution) % 360
      if myBot.scanDirection > myBot.huntEnd:
        myBot.post("Lost our target")
        myBot.resolution = 10
        myBot.hunting = False

  if myBot.heading == 0:
    # Heading east: scan 0 to 180
    if myBot.scanDirection > 180:
      myBot.scanDirection = 0

  if myBot.heading == 90:
    # Heading north: scan 90 to 270
    if myBot.scanDirection < 90 or myBot.scanDirection > 270:
      myBot.scanDirection = 90

  if myBot.heading == 180:
    # Heading west: scan 180 to 360
    if myBot.scanDirection < 180:
      myBot.scanDirection = 180

  if myBot.heading == 270:
    # Heading south: scan 270 to 90
    if myBot.scanDirection < 270 and myBot.scanDirection > 90:
      myBot.scanDirection = 270


# Do not change these lines
myBot.move = myMove
myBot.ping = myPing
myBot.setup = mySetup
myBot.main()

