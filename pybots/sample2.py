import userbot2
import random
import time

# Create global variables

myHeading = 45        # myHeading is the direction I want to go
mySpeed = 35          # mySpeed is the speed I want to go
myScanDirection = 0   # The direction to scan for enemies
myRunTimer = 0        # Timer for running fast after being scanned

# The mySetup function is run once at startup.
def mySetup():
  myBot.setName("Sample2")
  myBot.drive(myHeading, 35)
  print("setup ", myHeading)

def myPing(enemy):
  # If we got scanned, run for three seconds
  mySpeed = 100
  myBot.drive(myHeading, mySpeed)
  myBot.myRunTimer = time.time() + 3

def myMove():
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
  # If we're not turning or running, just mosey along
  else:
    if (time.time() > myRunTimer):
      mySpeed = 35
    myBot.drive(myHeading, mySpeed)

  # Scan
  result = myBot.scan(myScanDirection, 10)
  # If there's someone there, shoot at them
  if (result > 0):
    myBot.fire(myScanDirection, result)

  # Increment scan direction
  myScanDirection = (myScanDirection + 10) % 360

# Define class for our robot
class userbot(userbot2.bot):

  # Map our three functions to parent class
  def setup(self):
    mySetup()

  def move(self):
    myMove()

  def ping(self, enemy):
    myPing(enemy)

myBot = userbot()

myBot.main()

