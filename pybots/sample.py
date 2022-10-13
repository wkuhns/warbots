import userbot
import random
import time

# Create my robot - don't change this line
myBot = userbot.myBot

# Create variables - they should start with 'my'

myHeading = 0         # myHeading is the direction I want to go
mySpeed = 35          # mySpeed is the speed I want to go

myBot.myScanDirection = 0
myBot.myRunTimer = 0

def mySetup():
  global myHeading

  myBot.setName("Sample")
  myBot.drive(myHeading, 35)

def myPing(enemy):

  print ("Ouch! pinged by", enemy)
  mySpeed = 100
  myBot.drive(myHeading, mySpeed)
  myBot.myRunTimer = time.time() + 3

def myMove():
  global myHeading, mySpeed
  
  # See if we need to turn
  olddir = myHeading
  if (myBot.x > 900 and (myHeading > 270 or myHeading < 90)):
    myHeading = random.randint(90, 270)

  if (myBot.x < 100 and (myHeading < 270 and myHeading > 90)):
    myHeading = (myHeading + 180) % 360

  if (myBot.y > 900 and (myHeading > 0 and myHeading < 180)):
    myHeading = random.randint(180, 360)

  if (myBot.y < 100 and (myHeading > 180 and myHeading < 360)):
    myHeading = random.randint(0, 90)

  # If we're turning, set new scandir and slow down
  if myHeading != olddir:
    mySpeed = 15
    myBot.drive(myHeading, mySpeed)
  # If we're not turning, go as fast as we can
  else:
    if (time.time() > myBot.myRunTimer):
      mySpeed = 35
    myBot.drive(myHeading, mySpeed)

  # Scan and increment scan direction
  result = myBot.scan(myBot.myScanDirection, 10)
  if (result > 0):
    myBot.fire(myBot.myScanDirection, result)
  myBot.myScanDirection = (myBot.myScanDirection + 10) % 360

myBot.processMove = myMove
myBot.ping = myPing
myBot.setup = mySetup

userbot.main()

