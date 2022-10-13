# Test change from golden
#Test change from laptop
# Laptop change #2
# Test from new golden clone
import userbot
import random
import time

myBot = userbot.myBot

dir = 0
speed = 35
scanDirection = 0
runTimer = 0
hunting = False
shells = 4
resolution = 10
end = 0

def mySetup():
  myBot.setName("Charger")
  myBot.drive(dir,speed)

def myPing(enemy):
  global dir
  global speed
  global runTimer
  print ("Ouch! pinged by", enemy)
  speed = 100
  myBot.drive(dir, speed)
  runTimer = time.time() + 2

def myMove():
  global dir
  global speed
  global scanDirection
  global runTimer
  global hunting
  global shells
  global end

  # See if we need to turn
  olddir = dir
  if (myBot.x > 900 and (dir > 270 or dir < 90)):
    dir = 180

  if (myBot.x < 100 and (dir < 270 and dir > 90)):
    dir = 0

  if (myBot.y > 900 and (dir > 0 and dir < 180)):
    dir = 270

  if (myBot.y < 100 and (dir > 180 and dir < 360)):
    dir = 90

  # Scan

  if hunting == False:
    result = int(myBot.scan(scanDirection, 10))
    if (result > 0):
      hunting = True
      print ("Hunting", result)
      dir = scanDirection
      start = (scanDirection + 355) % 360
      end = (scanDirection + 5) % 360
      scanDirection = start
      if result > 200:
        speed = 100
      else:
        speed = 35

      myBot.drive(dir, speed)
    else:
      scanDirection = (scanDirection + 10) % 360

  if hunting == True:
    result = int(myBot.scan(scanDirection, 5))
    if (result > 0):
      myBot.fire(scanDirection, result)
      dir = scanDirection
      shells -= 1
      #shotwait = time.time() + 4
      scanDirection = (scanDirection + 350) % 360
      if result > 200:
        speed = 100
      else:
        speed = 35

      end = (scanDirection + 10) % 360

    else:
      scanDirection = (scanDirection + 5) % 360
      if scanDirection > end:
        hunting = False

  #scanDirection = (scanDirection + 10) % 360

  # If we're turning, set new scandir and slow down
  if dir != olddir:

    myBot.drive(dir, speed)
  # If we're not turning, go as fast as we can
  else:
    if (time.time() > runTimer):
      speed = 35
    myBot.drive(dir, speed)


myBot.processMove = myMove
myBot.ping = myPing
myBot.setup = mySetup

userbot.main()

