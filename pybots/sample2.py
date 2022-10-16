import userbot2
import random
import time

myBot = userbot2.myBot

# Create global variables

myBot.myHeading = 45        # myHeading is the direction I want to go
myBot.mySpeed = 35          # mySpeed is the speed I want to go
myBot.myScanDirection = 0   # The direction to scan for enemies
myBot.myRunTimer = 0        # Timer for running fast after being scanned

# The mySetup function is run once at startup.
def mySetup():
  myBot.setName("Sample2")
  myBot.drive(myBot.myHeading, 35)

def myPing(enemy):
  # If we got scanned, run for three seconds
  myBot.mySpeed = 100
  myBot.drive(myBot.myHeading, myBot.mySpeed)
  myBot.myRunTimer = time.time() + 3

def myMove():

  # See if we need to turn
  olddir = myBot.myHeading
  if (myBot.x > 900 and (myBot.myHeading > 270 or myBot.myHeading < 90)):
    myBot.myHeading = random.randint(90, 270)

  if (myBot.x < 100 and (myBot.myHeading < 270 and myBot.myHeading > 90)):
    myBot.myHeading = (myBot.myHeading + 180) % 360

  if (myBot.y > 900 and (myBot.myHeading > 0 and myBot.myHeading < 180)):
    myBot.myHeading = random.randint(180, 360)

  if (myBot.y < 100 and (myBot.myHeading > 180 and myBot.myHeading < 360)):
    myBot.myHeading = random.randint(0, 90)

  # If we're turning, set new scandir and slow down
  if myBot.myHeading != olddir:
    myBot.mySpeed = 15
    myBot.drive(myBot.myHeading, myBot.mySpeed)
  # If we're not turning or running, just mosey along
  else:
    if (time.time() > myBot.myRunTimer):
      myBot.mySpeed = 35
    myBot.drive(myBot.myHeading, myBot.mySpeed)

  # Scan
  result = myBot.scan(myBot.myScanDirection, 10)
  # If there's someone there, shoot at them
  if (result > 0):
    myBot.fire(myBot.myScanDirection, result)

  # Increment scan direction
  myBot.myScanDirection = (myBot.myScanDirection + 10) % 360

myBot.move = myMove
myBot.ping = myPing
myBot.setup = mySetup
myBot.main()

