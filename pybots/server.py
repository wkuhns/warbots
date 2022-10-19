import time
import socket
import selectors
import types
import random
import serverRobot
import tkinter as tk
from tkinter import ttk
from tkinter import *

QUANTA = 30
BOT_SIZE = 6
ARENA_SIZE = 800
STATUS_WIDTH = 400
colors = ["dodger blue", "lightgreen", "red", "yellow"]


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            recv_data = recv_data.decode("utf-8")
            # print(f"Command {data.outb!r} from {data.addr}")
            msgs = recv_data.split("|")
            for msg in msgs:
                if len(msg) < 3:
                    break
                cmds = msg.split(";")
                botindex = int(cmds[0]) - 1
                botcmd = cmds[1]
                if botcmd == "post":
                    botparm1 = cmds[2]
                    robots[botindex].post(botparm1)
                if botcmd == "scan":
                    botparm1 = cmds[2]
                    botparm2 = cmds[3]
                    robots[botindex].scan(int(botparm1), int(botparm2))
                if botcmd == "place":
                    botindex = place_bot(sock)
                    recv_data = ""
                    data.outb = ""
                    return
                if botcmd == "drive":
                    # print(f"Drive #{botindex}: {cmds[2]} {cmds[3]}")
                    botparm1 = cmds[2]
                    botparm2 = cmds[3]
                    robots[botindex].drive(int(botparm1), int(botparm2))
                    data.outb = ""
                    recv_data = ""
                    return
                if botcmd == "fire":
                    botparm1 = cmds[2]
                    botparm2 = cmds[3]
                    robots[botindex].fire(int(botparm1), int(botparm2))
                    data.outb = ""
                    recv_data = ""
                    return
                if botcmd == "set_name":
                    robots[botindex].name = cmds[2]
                    robots[botindex].panel.set_name(cmds[2])
                if botcmd == "setArmor":
                    if arena.status == 'S':
                        robots[botindex].set_armor(int(cmds[2]))
                if botcmd == "setScan":
                    if arena.status == 'S':
                        robots[botindex].scan_accuracy = int(cmds[2])
                if botcmd == "setDirection":
                    botparm1 = cmds[2]
                    robots[botindex].setSpeedGoal(int(botparm1))
                    # reply = "%d;%d" % (robots[botindex].x, 4)
                    data.outb = ""
                    recv_data = ""
                    return
                if botcmd == "set_autopilot":
                    robots[botindex].autopilot = True
                if botcmd == "set_autoscan":
                    robots[botindex].autoscan = True

        else:
            # Client has closed socket, close our end too
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
        data.outb = ""


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


# Subclass of tkinter.Canvas with positive Y axis and arena scaling
class MyCanvas(tk.Canvas):

    def __init__(self, window, height, width):
        super().__init__(window, height=f'{height}', width=f'{width}')
        self.height = height
        self.width = width
        self.xscale = width / 1000
        self.yscale = height / 1000
        self.starttime = time.time()
        self.gametime = 0
        self.status = "I"  # Initialized, Paused, Running, Finished

    def time():
        return time.time() - self.starttime

    def makebot(self, x, y, color):
        x = x * self.xscale
        y = self.height - y * self.yscale
        return super(MyCanvas, self).create_polygon(x - BOT_SIZE, y - BOT_SIZE, x - BOT_SIZE, y + BOT_SIZE, x + BOT_SIZE,
                                                    y + BOT_SIZE, x + BOT_SIZE, y - BOT_SIZE, fill=color, outline="Black",
                                                    width=1)

    # Move thing by x and y increments
    def move(self, thing, x, y):
        x = x * self.xscale
        y = y * self.yscale
        super(MyCanvas, self).move(thing, x, y * -1)

    def line(self, x1, y1, x2, y2, fill="black", width=1):
        x1 = x1 * self.xscale
        y1 = (1000 - y1) * self.yscale
        x2 = x2 * self.xscale
        y2 = (1000 - y2) * self.yscale
        return super(MyCanvas, self).create_line(x1, y1, x2, y2, fill=f"{fill}", width=f"{width}")

    def circle(self, x, y, r, fill=""):  # center coordinates, radius
        x0 = (x - r) * self.xscale
        y0 = (1000 - y - r) * self.yscale
        x1 = (x + r) * self.xscale
        y1 = (1000 - y + r) * self.yscale
        return super(MyCanvas, self).create_oval(x0, y0, x1, y1, fill=f"{fill}")

    def center(self, cir):
        coords = super(MyCanvas, self).coords(cir)
        x = (coords[0] + coords[2]) / 2 / self.xscale
        y = 1000 - ((coords[1] + coords[3]) / 2 / self.yscale)
        return [x, y]


# Window that frames the arena canvas
def create_frame(width, height):
    window = tk.Tk()
    window.title("Arena")
    window.geometry(f'{width}x{height}')
    return window


# Arena canvas
def create_arena(window, height, width):
    canvas = MyCanvas(window, height, width)
    canvas.configure(bg="Green")
    canvas.pack(expand=False)
    return canvas


def place_bot(sock):
    x = 0
    for q in range(0, 3):
        if quads[q].used == 0:
            x = 1

    if x == 0:
        print("Quadrant allocation error. Start over.")
        return 0

    # Pick a random quadrant
    q = random.randint(0, 3)
    while quads[q].used == 1:
        q = random.randint(0, 3)
    print(f"picked {q}")
    quads[q].used = 1
    r = len(robots)
    print(f"placing {r + 1}")
    x = random.randint(0, 300) + quads[q].x
    y = random.randint(0, 300) + quads[q].y

    robots.append(serverRobot.ServerRobot(r + 1, arena, robots))
    robots[r].place(sock, x, y)
    robots[r].panel = panels[r]
    robots[r].panel.populate(robots[r].name)
    # print(f"Bots: {robots[r].index}")

    print(f"placed {r}")
    return robots[r].index


class quad:
    def __init__(self):
        self.used = 0
        self.x = 0
        self.y = 0


quads = [quad(), quad(), quad(), quad()]
quads[0].x = 100
quads[0].y = 100
quads[1].x = 100
quads[1].y = 600
quads[2].x = 600
quads[2].y = 100
quads[3].x = 600
quads[3].y = 600


def make_panel(frame, row):
    recspec = [(2, 2), (STATUS_WIDTH - 2, ARENA_SIZE / 5 - 2)]
    mypanel = tk.Canvas(frame, width=STATUS_WIDTH, height=ARENA_SIZE / 5 - 2, bg="white", bd=1)
    mypanel.grid(column=1, row=row)
    mypanel.create_rectangle(recspec)
    # Label(mypanel, text=title, bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=131, y=3)
    return mypanel


class RobotPanel:
    def __init__(self, frame, index):
        self.botpanel = make_panel(frame, index)
        self.index = index
        print("Panel index", index)

    def populate(self, name):
        # Label at top

        # Speed display
        Label(self.botpanel, text='Speed', bg='white', font=('arial', 10, 'normal')).place(x=5, y=10)
        self.speed = Entry(self.botpanel)
        self.speed.config(width=4, justify=RIGHT, font='arial 10')
        self.speed.place(x=75, y=10)

        # Direction display
        Label(self.botpanel, text='Direction', bg='white', font=('arial', 10, 'normal')).place(x=5, y=40)
        self.dir = Entry(self.botpanel)
        self.dir.config(width=4, justify=RIGHT, font='arial 10')
        self.dir.place(x=75, y=40)

        # Motor Heat display
        Label(self.botpanel, text='Mtr Heat', bg='white', font=('arial', 10, 'normal')).place(x=5, y=70)
        self.mheat = Entry(self.botpanel)
        self.mheat.config(width=4, justify=RIGHT, font='arial 10')
        self.mheat.place(x=75, y=70)

        # Barrel Heat display
        Label(self.botpanel, text='Barrel', bg='white', font=('arial', 10, 'normal')).place(x=5, y=100)
        self.bheat = Entry(self.botpanel)
        self.bheat.config(width=4, justify=RIGHT, font='arial 10')
        self.bheat.place(x=75, y=100)

        # Health status bar
        Label(self.botpanel, text='Health', bg='white', font=('arial', 10, 'normal')).place(x=5, y=130)
        progessBarOne_style = ttk.Style()
        progessBarOne_style.theme_use('clam')
        progessBarOne_style.configure('progessBarOne.Horizontal.TProgressbar',
                                      foreground='#FF4040', background='#FF4040')

        self.progessBarOne = ttk.Progressbar(self.botpanel, style='progessBarOne.Horizontal.TProgressbar',
                                             orient='horizontal', length=300, mode='determinate', maximum=100,
                                             value=100)
        self.progessBarOne.place(x=75, y=130)

        # Message box
        self.msgBox = Text(self.botpanel, height=5, width=38, font=('Arial', '10'))
        self.msgBox.place(x=115, y=35)

    def set_name(self, name):
        print("Setting name", name)
        self.nameLabel = Label(self.botpanel, text=name, bg=colors[self.index - 1], font=('arial', 12, 'normal')).place(
            x=151, y=3)
        # self.nameLabel.config(text = name)

    def set_health(self, val):
        self.progessBarOne['value'] = val

    def set_mheat(self, val):
        self.mheat.delete(0, END)
        sval = "%.0f" % val
        self.mheat.insert(0, sval)

    def set_speed(self, val):
        self.speed.delete(0, END)
        sval = "%.0f" % val
        self.speed.insert(0, sval)

    def set_dir(self, val):
        self.dir.delete(0, END)
        sval = "%.0f" % val
        self.dir.insert(0, sval)

    def set_bheat(self, val):
        self.bheat.delete(0, END)
        sval = "%.0f" % val
        self.bheat.insert(0, sval)


def start_btn_click():
    if arena.gametime == 0:
        arena.starttime = time.time()
    arena.status = "R"
    post_message("Started")


def pause_btn_click():
    arena.status = "P"
    post_message("Paused")


def post_message(msg):
    msg = msg[:50]
    # self.panel.msgBox.insert('1.0', msg + '\n')
    arena.msgBox.insert(END, '\n' + msg)
    arena.msgBox.see(END)


# Create frame and arena - same size
frame = create_frame(ARENA_SIZE + STATUS_WIDTH + 2, ARENA_SIZE + 2)
arena = create_arena(frame, ARENA_SIZE, ARENA_SIZE)
arena.status = "S"

arena.grid(column=0, row=0, rowspan=5)

# Status panel Start button
panel_status = make_panel(frame, 0)
Button(panel_status, text='Start', bg='white', font=('arial', 12, 'normal'), command=start_btn_click).place(x=10, y=10)

# Status panel pause button
Button(panel_status, text='Pause', bg='white', font=('arial', 12, 'normal'), command=pause_btn_click).place(x=90, y=10)

# Status panel game time display
Label(panel_status, text='Game Time', bg='white', font=('arial', 10, 'normal')).place(x=250, y=15)
gTime = Entry(panel_status)
gTime.config(width=4, justify=RIGHT, font='arial 10')
gTime.place(x=350, y=20)

# Message box
arena.msgBox = Text(panel_status, height=6, width=52, font=('Arial', '10'))
arena.msgBox.place(x=10, y=50)

panels = []
for i in range(0, 4):
    panels.append(RobotPanel(frame, i + 1))

sel = selectors.DefaultSelector()
robots = []


def main():
    # bot = arena.makebot(750, 250, "lightgreen")

    starttime = time.time()

    HOST = "127.0.0.1"  # Symbolic name meaning all available interfaces
    PORT = 50007  # Arbitrary non-privileged port

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(f"Listening on {(HOST, PORT)}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    # try:
    while True:
        # don't block
        events = sel.select(timeout=-10)
        for key, mask in events:
            # listening socket
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)

        # Check if tournament is over
        players = 0
        winner = "none"
        for r in robots:
            if r.status == "A":
                players += 1
                winner = r.name

        # If game is running and 1 or fewer live robots, we're finished.
        if players <= 1 and arena.status == "R":
            arena.status = "F"
            post_message(f"Finished! The winner is {winner}.")
            for r in robots:
                r.clear_bomb()
        else:
            for r in robots:
                r.update()

        if arena.status == "R":
            arena.gametime = time.time() - arena.starttime
        # If we're paused increment start time
        if arena.status == "P":
            arena.starttime = time.time() - arena.gametime

        gTime.delete(0, END)
        sval = "%.0f" % arena.gametime
        gTime.insert(0, sval)
        frame.update()
        time.sleep(.033)

    # except KeyboardInterrupt:
    #  print("Caught keyboard interrupt, exiting")
    # finally:
    #  sel.close()
    #  sys.exit()


main()
