# These add capabilities that you might need. You can add others, but leave these.
import userRobot
import random

# This creates your robot. Don't change it.
mybot = userRobot.mybot

# Make changes below this line. *******************************************

# Create variables. Names are in the form mybot.xxx

mybot.heading = 45  # heading is the direction I want to go
mybot.scan_direction = 0  # The direction to scan for enemies


# The setup function is run once at startup. Edit this as desired
def setup():
    mybot.set_name("Simple")
    mybot.heading = 45
    mybot.drive(100, mybot.heading)
    mybot.set_armor(100)

# This gets run whenever your robot is scanned by an enemy.
# You get the ID of the enemy.
def ping(enemy):
    # Say 'Ouch'
    mybot.post("Ouch!")


# This gets run over and over about 20 times per second as long as your robot is alive.
# This is where you put almost all of your strategy.
def move():
    # Are we close to the east wall and heading more or less east?
    if mybot.x() > 900 and (mybot.heading > 270 or mybot.heading < 90):
        # Change to a random direction between 90 and 270 (west-ish)
        mybot.heading = random.randint(90, 270)

    # Same question, but avoid hitting west wall
    if mybot.x() < 100 and (270 > mybot.heading > 90):
        mybot.heading = (mybot.heading + 180) % 360

    # Avoid south wall
    if mybot.y() > 900 and (0 < mybot.heading < 180):
        mybot.heading = random.randint(180, 360)

    # Avoid north wall
    if mybot.y() < 100 and (180 < mybot.heading < 360):
        mybot.heading = random.randint(0, 90)

    mybot.drive(100, mybot.heading)

    # Scan
    my_range = mybot.scan(mybot.scan_direction, 10)

    # If there's someone there, shoot at them
    if my_range > 0:
        mybot.fire(mybot.scan_direction, my_range)
        mybot.post("Bang!")

    # Increment scan direction
    mybot.scan_direction = (mybot.scan_direction + 10) % 360


# Do not change below this line ************************************************
mybot.move = move
mybot.ping = ping
mybot.setup = setup
mybot.main()
