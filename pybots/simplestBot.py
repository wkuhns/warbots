# These add capabilities that you might need. You can add others, but leave these.
import userRobot

# This creates your robot. Don't change it.
mybot = userRobot.mybot

# Make changes below this line. *******************************************
# Create variables. Names are in the form mybot.myXxxxxxxx


# The setup function is run once at startup. Edit this as desired
def setup():
    mybot.set_name("Simplest")
    mybot.set_autopilot()
    mybot.set_autoscan()
    mybot.set_armor(10)


# This gets run whenever your robot is scanned by an enemy.
# You get the ID of the enemy.
def ping(enemy):
    # Complain about being scanned
    mybot.post(f"That dirty dog {enemy} scanned me")


# This gets run over and over about 20 times per second as long as your robot is alive.
# This is where you put almost all of your strategy.
def move():
    pass        # 'pass' means don't do anything since we have autopilot and autoscan


# Do not change below this line ************************************************
mybot.move = move
mybot.ping = ping
mybot.setup = setup
mybot.main()
