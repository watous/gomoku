from tkinter import *
from itertools import product
from random import choice

from gomoku import *
from player import Player
try:
    from skins import *
    SKINS_AVAILABLE = True
except ImportError as e:
    if e.name == "PIL":
        SKINS_AVAILABLE = False
        print("It seems that you don't have PIL installed. Skins won't be available.")
    else:
        raise e

from megabot import Megabot
# add your computer player here:
bots = [Megabot]

"""
GUI instructions:

click to play
press ctrl+z to undo a move
when game is over, click to start a new game
rightclick to open settings

in settings: if you select more than one option in PLAYERS,
    random of the selected options will be chosen for each games
"""

### APPEARANCE ###

## BOARD FUNCTIONS

# board(canvas, left, top, size, width, height)
#   On `canvas`, draw a game board such that it will have
#   `width` positions for stones horizontally, `height` vertically,
#   the leftmost and uppermost position will have center in `left, top`
#   and two adjacent positions will be separated by distance `size`.

def paperlike(canvas, left, top, size, width, height):
    canvas.config(bg="white")
    left -= 0.5*size
    top -= 0.5*size
    for i in range(width + 1):
        canvas.create_line(
            left + i * size, top,
            left + i * size, top + height * size
            )
    for i in range(height + 1):
        canvas.create_line(
            left,                top + i * size,
            left + width * size, top + i * size
            )

def standard(canvas, left, top, size, width, height):
    canvas.config(bg="orange4")
    for i in range(width):
        canvas.create_line(
            left + i * size, top,
            left + i * size, top + (height - 1) * size
            )
    for i in range(height):
        canvas.create_line(
            left,                      top + i * size,
            left + (width - 1) * size, top + i * size
            )

## SEPARATE HIGHLIGHT FUNCTIONS

# highlight(canvas, x, y, half_size)
#   `x, y` is the center of a square with side-length `2*half_size`,
#   highlight the mark/stone on `canvas` on that square
#   as last played and return a list of all drawn shapes.

# use `@add_highlight(highlight_func)` to a mark function to apply the highlight


def square_highlight(fill="#eee", outline="", line_width=2):
    def f(canvas, x, y, half_size):
        return [canvas.create_rectangle(x - half_size + 1, y - half_size + 1,
                                        x + half_size, y + half_size,
                                        fill=fill, outline=outline, width=line_width)]
    return f

def add_highlight(below=None, above=None):
    def decorator(mark_func):
        def f(*args, **kwargs):
            highlight1 = [] if below is None else below(*args, **kwargs)
            mark, highlight2 = mark_func(*args, **kwargs)
            highlight3 = [] if above is None else above(*args, **kwargs)
            return (mark, highlight1 + highlight2 + highlight3)
        return f
    return decorator

## MARK FUNCTIONS

# mark(canvas, x, y, half_size)
#   `x, y` is the center of a square with side-length `2*half_size`,
#   draw a mark/stone on `canvas` to that square. Can also draw a separate 
#   highlight to be deleted after next turn. Return tuple
#   (list of all drawn shapes of stone, list of drawn shapes of highlight).

def stone(color, highlight_color="orange"):
    def f(canvas, x, y, half_size):
        half_size *= 0.8
        mark = [canvas.create_oval (x - half_size, y - half_size,
                                    x + half_size, y + half_size,
                                    fill=color, outline="")]
        half_size *= 0.3
        highlight = [canvas.create_oval (x - half_size, y - half_size,
                                         x + half_size, y + half_size,
                                         fill=highlight_color, outline="")]

        return (mark, highlight)
    return f

@add_highlight(square_highlight(fill="#ddf"))
def cross(canvas, x, y, half_size):
    result =  []
    half_size *= 0.7
    kwargs = dict(fill = "blue", width = half_size/4)
    result.append(canvas.create_line(x - half_size, y - half_size,
                                     x + half_size, y + half_size, **kwargs))
    result.append(canvas.create_line(x - half_size, y + half_size,
                                     x + half_size, y - half_size, **kwargs))
    return (result, [])

@add_highlight(square_highlight(fill="#fdd"))
def circle(canvas, x, y, half_size):
    result = []
    half_size *= 0.7
    kwargs = dict(outline = "red", width = half_size/4)
    result.append(canvas.create_oval(x - half_size, y - half_size,
                                     x + half_size, y + half_size, **kwargs))
    return (result, [])

@add_highlight(square_highlight(fill="#dfd"))
def triangle (canvas, x, y, half_size):
    result = []
    half_size *= 0.7
    kwargs = dict(outline = "green", fill="", width = half_size/4)
    result.append(canvas.create_polygon(x + half_size, y + 3**0.5/2*half_size,
                                        x - half_size, y + 3**0.5/2*half_size,
                                        x, y - 3**0.5/2*half_size, **kwargs))
    return (result, [])

# add appearance options here:
appearance_options = {
    "paper and pencil": (paperlike,
                         (cross, circle, triangle),
                         "black"),
    "go": (standard,
           (stone("black"), stone("white"), stone("gray50"), stone("gray75"), stone("gray25")),
           "orange"),
    }
if SKINS_AVAILABLE: appearance_options.update({
    "skins/example.png": Skin("skins/example.png"),
    "custom skin": CustomSkin(),
    })
# {name of the option: (board function,
#                       tuple of mark functions,
#                       color of winning line), ...}

### Main Tkinter class

class App:
    """Run a gomoku app."""
    def __init__(self, master, canvas_width=300, canvas_height=None,
                appearance_options=appearance_options,
                rule_options=rule_options, num_players=[2,3],
                x=15, y=None, win_length=5, freestyle=False, #these can be changed in settings
                ):
        """
Args:
    master: tkinter root
    canvas_width: width of the canvas, on which the borad is drawn
    canvas_height: height of the canvas, same as `canvas_width` if None
    appearance_options (dict): {name of the option:
        (board function, tuple of mark functions, color of winning line), ...}
    rule_options: list of rule functions, see gomoku.py
    num_players: (a single int of a list of ints) permitted numbers of players
    x: width of board
    y: height of board, same as `x` if None
    win_length: number of stones in a row to win
    freestyle: whether rows longer than win_length win
"""
        self.master = master
        self.x = IntVar()
        self.y = IntVar()
        self.x.set(x) 
        self.y.set(y if y is not None else x)
        self.win_length = IntVar()
        self.win_length.set(win_length)
        self.freestyle = BooleanVar()
        self.freestyle.set(freestyle)

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height if canvas_height is not None else self.canvas_width

        self.history = []
        
        self.appearance_options = appearance_options 
        self.appearance = StringVar()
        self.appearance.set(next(iter(self.appearance_options.keys())))
        

        self.click_var = BooleanVar() #only to change after click so that MyPlayer can notice that

        self.last_turn_highlight = []
        self.win_line = []

        class Me(Player):
            def turn(me):
                self.master.wait_variable(self.click_var)
                while not me.play((self.click_x,self.click_y)):
                    if not self.click_var.get():
                        return
                    self.master.wait_variable(self.click_var)
                    

            def choose(me):
                self.click_x = None #this loop must run at least once:
                while not (self.click_x,self.click_y) in me.game.plan:
                    self.master.wait_variable(self.click_var)
                    if not self.click_var.get():
                        return
                return me.game.plan[(self.click_x,self.click_y)]

        self.player = Me
        self.player_options = []
        if not isinstance(num_players, list):
            num_players = [num_players]
        for i in num_players:
            self.player_options.extend(list(product([self.player] + bots, repeat=i)))

        self.rule_options = rule_options
        self.rule = IntVar()
        self.rule.set(0)

        self.click_x = self.click_y = None

        self.prepare_tkinter()
        self.create_settings()
        self.new_game()
        self.draw_board()  
        self.game.run()

    def prepare_tkinter(self):
        self.master.title("Gomoku")
        self.master.iconbitmap("images/icon.ico")
        
        self.canvas = Canvas(root, bg = "white", width = canvas_width, height = canvas_height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonRelease-1>", self.click)
        
        self.master.bind("<Button-3>", lambda e: self.settings.deiconify())
        self.master.bind("<F10>", lambda e: (self.settings.deiconify(), self.settings.update()))
        self.master.bind("<F5>", self.reset)
        self.master.bind("<Control-r>", self.reset)
        self.master.bind("<Control-z>", self.undo)
        self.master.bind_all("<Escape>", lambda e: self.settings.withdraw())
        self.master.protocol("WM_DELETE_WINDOW", self.kill)

    def kill(self):
        self.game.quit()
        self.click_var.set(False)
        self.master.quit()
        self.master.destroy()
        
    def create_settings(self):
        self.settings = Toplevel()
        self.settings.withdraw()                  
        self.settings.title("Settings")
        self.settings.iconbitmap("images/settings.ico")
        #self.settings.geometry(f"+{self.master.winfo_x() + 50}+{self.master.winfo_y() + 50}")
        self.settings.protocol("WM_DELETE_WINDOW", self.settings.withdraw) #don't close the settings, just hide them
        self.settings.bind("<Return>", self.reset)

        frame = Frame(self.settings, padx=10)
        Label(frame, text="PLAYERS").pack(anchor="w")
        self.POlist = Listbox(frame, selectmode="extended", width=30, background="white", selectbackground="gray75", selectforeground="black", exportselection=0)
        for i,c in enumerate(self.player_options):
            self.POlist.insert(END, ", ".join(x.__name__ for x in c))
        self.POlist.pack(anchor="w", fill="both", expand="yes", side="left")
        frame.pack(side="right", anchor="n", fill="both", expand="yes",)

        Label(self.settings, text="APPEARANCE", padx=10).pack(anchor="w")
        for i in self.appearance_options:
            Radiobutton(self.settings, text=i,
                        variable=self.appearance, value=i).pack(anchor="w", padx=10)

        Label(self.settings, text="RULES", padx=10).pack(anchor="w")
        for i,c in enumerate(self.rule_options):
            Radiobutton(self.settings, text=c.__name__,
                        variable=self.rule, value=i).pack(anchor="w", padx=10)

        
        Label(self.settings, text="Length of winning row:", padx=10).pack(anchor="w")
        frame = Frame(self.settings)
        Entry(frame, width=5, textvariable=self.win_length).pack(side="left", anchor="w")
        Checkbutton(frame, text="or longer", variable=self.freestyle).pack(anchor="w")
        frame.pack(anchor="w", pady=5, padx=20)

        frame = Frame(self.settings)
        Label(frame, text="Width").pack(side="left", anchor="w")
        Entry(frame, width=5, textvariable=self.x).pack(side="left")
        Label(frame, text="; Height").pack(side="left", anchor="w")
        Entry(frame, width=5, textvariable=self.y).pack(side="left")
        frame.pack(anchor="w", padx=10)

        Button(self.settings, text="New Game", command=self.reset).pack(pady=10)

    def new_game(self, *args, **kwargs):
        self.game = Gomoku(self.player_options[choice(self.POlist.curselection() or [0])],
                              dimensions=(self.x.get(),self.y.get()),
                              win_length=self.win_length.get(),
                              rule=self.rule_options[self.rule.get()],
                              freestyle=self.freestyle.get(),
                              spectators=[self])
        self.mark_funcs = self.appearance_options[self.appearance.get()][1]
        self.win_line_color = self.appearance_options[self.appearance.get()][2]

    def draw_board(self):
        width = self.x.get()
        height = self.y.get()
        size = min((self.canvas_width - 10) / width,
                   (self.canvas_height - 10) / height)
        left = (self.canvas_width + (1 - width) * size) / 2
        top = (self.canvas_height + (1 - height) * size) / 2
        self.appearance_options[self.appearance.get()][0](self.canvas, left, top, size, width, height) 

        self.board_left = left
        self.board_top = top
        self.square_size = size

    def to_canvas_pos(self, x, y):
        return(self.board_left + x * self.square_size,
                self.board_top + y * self.square_size)

    def to_board_pos(self, x, y):
        return(int(round((x - self.board_left) / self.square_size)),
                int(round((y - self.board_top) / self.square_size)))

    def view(self):
        if len(self.mark_funcs) <= self.game.plan[self.game.history[-1]]:
            raise IndexError("more players than player marks")
        mark_func = self.mark_funcs[self.game.plan[self.game.history[-1]]]
        x, y = self.game.history[-1]
        x, y = self.to_canvas_pos(x, y)
        half_size = self.square_size / 2
        self.canvas.delete(self.last_turn_highlight)
        mark, self.last_turn_highlight = mark_func(self.canvas, x, y, half_size)
        self.history.append(mark)
        #self.master.wait_variable(self.click_var) #for games of bots only

    def review(self, position, player_index):
        for i in self.history.pop():
            self.canvas.delete(i)

    def game_over(self):
        if self.game.won != -1: #if it is not draw
            #mark the winning row
            winplace1 = self.to_canvas_pos(*self.game.winning_row[0])
            winplace2 = self.to_canvas_pos(*self.game.winning_row[1])
            self.win_line = [self.canvas.create_line((*winplace1, *winplace2), width=max(2,self.square_size/15), fill=self.win_line_color)]
        
    def click(self, event):
        if self.settings.state() == "normal":
            self.settings.withdraw()
            return
        if self.game.won is not None:
            self.reset()
            return
        canvas_x = event.x; canvas_y = event.y
        self.click_x, self.click_y = self.to_board_pos(canvas_x, canvas_y)
        self.click_var.set(True)
        
    def undo(self, event=None):
        for e in self.last_turn_highlight:
            self.canvas.delete(e)
        for e in self.win_line:
            self.canvas.delete(e)
        i = 1
        while i < len(self.game.players) and i < len(self.game.history) and type(self.game.players[self.game.plan[self.game.history[-i]]]) != self.player:
            i += 1
        self.game.undo(i)
        self.click_var.set(True)
           
    def reset(self, event=None):
        self.settings.withdraw()
        self.game.quit()
        self.click_var.set(False)
        self.canvas.delete(ALL)
        self.history = []
        self.new_game()
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.draw_board()
        self.master.after(0, self.game.run) # waiting things execute now


if __name__ == "__main__":
    x = 15
    y = x
    win_length = 5
    canvas_width = 500
    canvas_height = 700#canvas_width
    
    root = Tk()
    app = App(root,
              x=x, y=y, win_length=win_length, num_players=[2,3],
              canvas_width = canvas_width, canvas_height = canvas_height)
    root.mainloop()
