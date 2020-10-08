from gomoku import *
from player import Player
from megabot import Megabot as Bot

if False: #if you want colors
    try:
        from colorama import init, Fore
    except ImportError:
        print("colorama is not installed")
        class Fore: RED=BLUE=RESET=""
    else:
        init (autoreset=True)
else:
    class Fore: RED=BLUE=RESET=""


class ConsolePlayer(Player):
    def __init__(self, game, symbols="xo", empty="."):
        self.game = game
        self.symbols = symbols
        self.labels = None
        if len(self.game.dimensions) == 2:
            self.labels = [[]]
            for i in range(self.game.dimensions[1]):
                new = str(i+1)
                self.labels[0].append (" "*(3-len (new))+new+" ")               
            self.labels.append([4*" " + "a b c d e f g h i j k l m n o p q r s t u v w x y z"[:2*(self.game.dimensions  [0])]+"\n"])
        self.seps = [[" "],
                     [" ","\n"],
                     [" ","  ","\n"],
                     [" ","  ","\n","\n\n"]
                     ][len(self.game.dimensions)-1]
        self.empty = empty

    def visualize (self):
        text = ""
        if self.labels:
            for i in self.labels[::-1]:
                text += i[0]
        lend = len (self.game.dimensions)
        pos = [0 for _ in range (lend)]
        while True:
            if tuple(pos) in self.game.plan:
                text += self.symbols[self.game.plan[tuple(pos)]]
            else:
                text += self.empty
            i = 0
            while pos [i]+1 >= self.game.dimensions [i]:
                pos [i] = 0
                i += 1
                if i >= lend:
                    print("\n"+text+"\n")
                    return
            pos [i] += 1
            text += self.seps [i]
            if self.labels:
                while i > 0:
                    text += self.labels[i-1][pos [i]]
                    i -= 1

    def game_over(self):
        self.visualize()
        if self.game.win == -1:
            print("REMÍZA")
        elif self.game.players[self.game.win] == self:
            print("VÝHRA")
        else:
            print("PROHRA")

    def review(self, _, __):
        return self.visualize()
    
    def turn(self):
        self.visualize()
        while True: #just waiting for correct input
            x=self.stin(keystart="*")
            if isinstance(x,str):
                if x in ("b","z"): #undo
                    self.game.undo(2)
                if x=="e": #quit game
                    self.game.destroy()
                    return
                    #fails if you try to undo after that (game.winplace = None)
            elif self.play(x):
                return

    def choose(self):
        self.visualize()
        while True:
            x = input("/".join(self.symbols)+" ")
            if x in self.symbols:
                return self.symbols.index(x)
        

    def stin (self,keystart=False,laststyle=lambda x:x,last=None):
        if last is None:
            if self.game.history:
                last=self.game.history[-1]
                last=" "+chr(last[0]+97)+str(last[1]+1).ljust (3)
            else:
                last=" "*5
        while True:
            text=input(laststyle(last)).lower()
            if keystart and text.startswith (keystart):
                return text [len(keystart):]
            pos=[]
            i=0
            last=0 #last non-numeric character
            odd=False #True if len(pos) is odd
            while i < len(text): #parsing input, searching for letters and numbers
                if not text[i].isnumeric():
                    if last < i:
                        pos.append(int(text[last:i])-1)   
                        odd=not odd
                    if text[i].isalpha():
                        if odd: #changing order of coordinates (12f => f12), but isn't really good
                            pos.insert(-2,ord(text[i])-97)
                        else:
                            pos.append(ord(text[i])-97)
                        odd=not odd
                    last=i+1
                i += 1
            if last < i:
                pos.append(int(text[last:i])-1)
            return tuple(pos)

while True:
    rules = normal if input("bez swapu? ") else swap
    players = [Bot, ConsolePlayer]
    if input("začít? "):
        players = players [::-1]
    p = Gomoku(players=players, rules=rules, dimensions=[15,15], winlength=5)
    p.run()
