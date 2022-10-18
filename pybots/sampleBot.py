# These add capabilities that you might need. You can add others, but leave these.
import userRobot
import random
import time

# This creates your robot. Don't change it.
myBot = userRobot.myBot

# Make changes below this line. *******************************************

# Create variables. Names are in the form myBot.myXxxxxxxx

myBot.myHeading = 45        # myHeading is the direction I want to go
myBot.mySpeed = 35          # mySpeed is the speed I want to go
myBot.myScanDirection = 0   # The direction to scan for enemies
myBot.myRunTimer = 0        # Timer for running fast after being scanned

# The mySetup function is run once at startup. Edit this as desired
def mySetup():
  myBot.setName("Sample")
  myBot.drive(35, myBot.myHeading)
  myBot.post("Alive!")

# This gets run whenever your robot is scanned by an enemy. You get the ID of the enemy.
def myPing(enemy):
  # If we got scanned, run for three seconds
  myBot.post(f"Ouch: scanned by {enemy}")
  myBot.mySpeed = 100
  myBot.drive(myBot.mySpeed, myBot.myHeading)
  myBot.myRunTimer = time.time() + 3

# This gets run over and over about 20  times per second as long as your robot is alive.
# This is where you put almost all of your strategy.
def myMove():

  # See if we need to turn - remember our original planned direction 
  olddir = myBot.myHeading

  # Are we close to the east wall and heading more or less east?
  if (myBot.x > 900 and (myBot.myHeading > 270 or myBot.myHeading < 90)):
    # Change to a random direction between 90 and 270 (west-ish)
    myBot.myHeading = random.randint(90, 270)

  # Same question, but avoid hitting west wall
  if (myBot.x < 100 and (myBot.myHeading < 270 and myBot.myHeading > 90)):
    myBot.myHeading = (myBot.myHeading + 180) % 360

  # Avoid south wall
  if (myBot.y > 900 and (myBot.myHeading > 0 and myBot.myHeading < 180)):
    myBot.myHeading = random.randint(180, 360)

  # Avoid north wall
  if (myBot.y < 100 and (myBot.myHeading > 180 and myBot.myHeading < 360)):
    myBot.myHeading = random.randint(0, 90)

  # If we have a new direction, set new scandir and slow down
  if myBot.myHeading != olddir:
    myBot.mySpeed = 15
    myBot.drive(myBot.mySpeed, myBot.myHeading)

  # If we're not turning or running, just mosey along
  else:
    if (time.time() > myBot.myRunTimer):
      myBot.mySpeed = 35
    myBot.drive(myBot.mySpeed, myBot.myHeading)

  # Scan
  result = myBot.scan(myBot.myScanDirection, 10)

  # If there's someone there, shoot at them
  if (result > 0):
    myBot.fire(myBot.myScanDirection, result)
    myBot.post("Bang! %d %d" % (myBot.myScanDirection, result))

  # Increment scan direction
  myBot.myScanDirection = (myBot.myScanDirection + 10) % 360

# Do not change these lines
myBot.move = myMove
myBot.ping = myPing
myBot.setup = mySetup
myBot.main()

