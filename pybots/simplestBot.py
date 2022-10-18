# These add capabilities that you might need. You can add others, but leave these.
import userRobot
import random
import time

# This creates your robot. Don't change it.
myBot = userRobot.myBot

# Make changes below this line. *******************************************

# Create variables. Names are in the form myBot.myXxxxxxxx

# The mySetup function is run once at startup. Edit this as desired
def mySetup():
  myBot.setName("Simplest")
  myBot.setAutopilot()
  myBot.setAutoscan()

# This gets run whenever your robot is scanned by an enemy. 
# You get the ID of the enemy.
def myPing(enemy):
  # Say 'Ouch'
  #myBot.post("That dirty dog %d scanned me" % (enemy))
  myBot.post(f"That dirty dog {enemy} scanned me")

# This gets run over and over about 20 times per second as long as your robot is alive.
# This is where you put almost all of your strategy.
def myMove():
  pass  

# Do not change below this line ************************************************
myBot.move = myMove
myBot.ping = myPing
myBot.setup = mySetup
myBot.main()

