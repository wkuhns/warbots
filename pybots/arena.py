import tkinter
import time
 
class myCanvas(tkinter.Canvas):
    
  def makeBot(self, x, y, color):
    return super(myCanvas, self).create_polygon(x-3,y-3, x-3,y+3, x+3,y+3, x+3,y-3, fill="Red", outline="Black", width=1)
    #return super(myCanvas, self).create_polygon(50,50, 50,55, 55,55, 55,50, fill="red", outline="Black", width=1)

  def move(self,thing,x,y):
    super(myCanvas, self).move(thing,x,y*-1)

def createFrame():
  Window = tkinter.Tk()
  Window.title("Arena")
  Window.geometry('1050x1050')
  return Window
 

def createArena(Window):
  #canvas = tkinter.Canvas(Window, height=1000, width=1000)
  canvas = myCanvas(Window, height=1000, width=1000)
  canvas.configure(bg="Blue")
  canvas.pack(expand=False)
  return canvas

frame = createFrame()
arena = createArena(frame)
#bot = arena.create_polygon(50,50, 50,55, 55,55, 55,50, fill="red", outline="Black", width=1)
bot = arena.makeBot(50, 50, "Blue")

while True:
  arena.move(bot,0,1)
  frame.update()
  time.sleep(.033)


#animate_ball(frame,arena, Ball_min_movement, Ball_min_movement)
