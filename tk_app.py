from tkinter import *
from gomoku import *
from player import Player
from megabot import Megabot

from itertools import product
from random import choice


## SYMBOLS

def cross(canvas, x, y, size): #x, y jsou střed políčka, size je velikost políčka
    result =  []
    half_size = size / 2 - 3
    kwargs = dict(fill = "blue", width = 3)
    result.append(canvas.create_line((x - half_size, y - half_size,
                                        x + half_size, y + half_size), **kwargs))
    result.append(canvas.create_line((x - half_size, y + half_size,
                                        x + half_size, y - half_size), **kwargs))
    return result

def circle(canvas, x, y, size):
    result = []
    half_size = size / 2 - 4
    kwargs = dict(outline = "red", width = 3)
    result.append(canvas.create_oval((x - half_size, y - half_size,
                                        x + half_size, y + half_size), **kwargs))
    return result

def triangle (canvas, x, y, size):
    result = []
    half_size = size / 2 - 3
    kwargs = dict(outline = "green", fill="", width = 3)
    result.append(canvas.create_polygon((x + half_size, y + 3**0.5/2*half_size,
                                         x - half_size, y + 3**0.5/2*half_size,
                                         x, y - 3**0.5/2*half_size), **kwargs))
    return result


## Main Tkinter class

#n = 0

class App:
    def __init__(self, master, symbols=[cross, circle],
                  x=15, y=None, winlength=5,
                  canvas_width=300, canvas_height=None):
        self.master = master
        self.x = IntVar()
        self.y = IntVar()
        self.x.set(x) #počet políček ve vodorovném směru
        self.y.set(y if y is not None else x)
        self.winlength = IntVar()
        self.winlength.set(winlength)

        self.canvas_width = canvas_width
        self.canvas_height = canvas_height if canvas_height is not None else self.canvas_width

        self.history = []
        self.symbols = symbols

        self.click_var = BooleanVar() #jedině proto, aby se změnila po kliknutí, aby to MyPlayer zachytil

        self.last_turn_highlight = None

        class Me(Player):
            def turn(me):
                #global n
                #m=n
                #print("turn",n,self.game.win)
                #n+=1
                self.master.wait_variable(self.click_var)
                while not me.play((self.click_x,self.click_y)):
                    #print("attempt",m)
                    self.master.wait_variable(self.click_var)
                #print("played",m)
            def choose(me):
                self.master.wait_variable(self.click_var)
                while not (self.click_x,self.click_y) in me.game.plan:
                    self.master.wait_variable(self.click_var)
                return me.game.plan[(self.click_x,self.click_y)]

        self.player = Me
        self.player_options = list(product([self.player, Megabot], repeat=2))

        self.rules = IntVar()
        self.rules.set(0)
        
        self.create_settings()
        self.widgets()

        self.new_game()
        self.prepare_plan()  
        self.game.run()
        
    def new_game(self, *args, **kwargs):
        self.game = Gomoku(self.player_options[choice(self.POlist.curselection() or [0])],
                              dimensions=(self.x.get(),self.y.get()),
                              winlength=self.winlength.get(),
                              rules=rules_options[self.rules.get()])
        self.game.spectators.append(self)
        
    def create_settings(self):
        self.settings = Toplevel(self.master)
        self.settings.withdraw()
        self.settings.protocol("WM_DELETE_WINDOW", self.settings.withdraw)
                               
        self.settings.title("Nastavení")
        self.settings.geometry(f"+{self.master.winfo_x() + 50}+{self.master.winfo_y() + 50}")
        self.settings.iconbitmap("images/settings.ico")

        label = Label(self.settings, text="HRÁČI", padx=10)
        label.pack(anchor="w")

        self.POlist = Listbox(self.settings, selectmode="extended")
        for i,c in enumerate(self.player_options):
            self.POlist.insert(END, ", ".join(x.__name__ for x in c))
        self.POlist.pack(anchor="w", padx=10, fill="both", expand=YES)
            
        label = Label(self.settings, text="PRAVIDLA", padx=10)
        label.pack(anchor="w")
        for i,c in enumerate(rules_options):
            radio_button = Radiobutton(self.settings, text = c.__name__, variable = self.rules, value = i,)
            radio_button.pack(anchor="w", padx=10)

        frame = Frame(self.settings)
        label = Label(frame, text="Délka výhry", padx=10)
        label.pack(side="left", anchor="w")
        entry = Entry(frame, width=5, textvariable=self.winlength)
        entry.pack(side="left")
        frame.pack(anchor="w", pady=5)

        frame = Frame(self.settings)
        label = Label(frame, text="Šířka")
        label.pack(side="left", anchor="w")
        entry = Entry(frame, width=5, textvariable=self.x)
        entry.pack(side="left")
        label = Label(frame, text="; Výška")
        label.pack(side="left", anchor="w")
        entry = Entry(frame, width=5, textvariable=self.y)
        entry.pack(side="left", pady=5)
        frame.pack(anchor="w", padx=10)

        reset_button = Button(self.settings, text = "Začít znovu", command = self.reset)
        reset_button.pack(pady=10)
            
    def widgets(self):
        self.canvas = Canvas(root, bg = "#ffffff", width = canvas_width, height = canvas_height)
        self.canvas.pack()
        
        self.master.iconbitmap("images/icon.ico")
        
        self.canvas.bind("<ButtonRelease-1>", self.click)
        self.master.bind("<Button-3>", lambda e: self.settings.deiconify())
        self.master.bind("<F5>", self.reset)
        self.master.bind("<Control-z>", self.undo)
        self.master.bind_all("<Escape>", lambda e: self.settings.withdraw())
    
    def prepare_plan(self):
        size = min((self.canvas_width - 5) / self.x.get(),
                   (self.canvas_height - 5) / self.y.get())
        plan_left = (self.canvas_width - self.x.get() * size) / 2
        plan_top = (self.canvas_height - self.y.get() * size) / 2
        plan = []
        for i in range(self.x.get() + 1):
            plan.append(self.canvas.create_line(
                (plan_left + i * size, plan_top,
                 plan_left + i * size, plan_top + self.y.get() * size)
                ))
        for i in range(self.y.get() + 1):
            plan.append(self.canvas.create_line(
                (plan_left,                 plan_top + i * size,
                 plan_left + self.x.get() * size, plan_top + i * size)
                ))
        self.plan = plan
        self.plan_left = plan_left
        self.plan_top = plan_top
        self.square_size = size

    def to_canvas_pos(self, x, y):
        return(self.plan_left + (x + 0.5) * self.square_size,
                self.plan_top + (y + 0.5) * self.square_size)

    def to_plan_pos(self, x, y):
        return(int((x - self.plan_left) // self.square_size),
                int((y - self.plan_top) // self.square_size))

    def view(self):
        self.draw_new()
        #self.master.wait_variable(self.click_var)
    
    def click(self, event):
        if self.settings.state() == "normal":
            self.settings.withdraw()
            return
        if self.game.win is not None:
            self.reset()
            return
        canvas_x = event.x; canvas_y = event.y
        self.click_x, self.click_y = self.to_plan_pos(canvas_x, canvas_y)
        self.click_var.set(True)

    def draw_new(self, last=1):
        for i in range(last, 0, -1):
            symbol = self.symbols[self.game.plan[self.game.history[-i]]]
            x, y = self.game.history[-i]
            x, y = self.to_canvas_pos(x, y)
            if self.last_turn_highlight:
                self.canvas.delete(self.last_turn_highlight)
            halfsize = self.square_size // 2
            self.last_turn_highlight = self.canvas.create_rectangle(x - halfsize + 1, y - halfsize + 1,
                                                                      x + halfsize, y + halfsize,
                                                                      fill = "#e0e0e0", outline = "")
            self.history.append(symbol(self.canvas,
                                    x,y,
                                    self.square_size)
                                 )


    def game_over(self):
        if self.game.win != -1: #není-li to remíza
            #škrtnutí
            winplace1 = self.to_canvas_pos(*self.game.winplace[0])
            winplace2 = self.to_canvas_pos(*self.game.winplace[1])
            self.canvas.create_line((*winplace1, *winplace2), width = 3)

    def reset(self, event = None):
        self.settings.withdraw()
        self.click_var.set(True)
        self.canvas.delete(ALL)
        self.history = []
        self.game.destroy()
        self.new_game()
        
        self.prepare_plan()
        self.game.run()
        
    def undo(self, event):
        if self.last_turn_highlight:
            self.canvas.delete(self.last_turn_highlight)
        return self.game.undo(2)

    def review(self, pos, player_index):
        for i in self.history.pop():
            self.canvas.delete(i)


if __name__ == "__main__":
    symbols = [cross, circle, triangle]
    x = 15
    y = x
    winlength = 5
    canvas_width = 400
    canvas_height = canvas_width
    
    root = Tk()
    root.title("Piškvorky")
    app = App(root, x = x, y = y, winlength = winlength, symbols = symbols, canvas_width = canvas_width, canvas_height = canvas_height)
    root.mainloop()
