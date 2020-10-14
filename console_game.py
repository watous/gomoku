from gomoku import *
from player import Player
from megabot import Megabot as Bot

"""Enter *z or *b to undo, *e or *q to end game"""

def console_player (stones=["x","o"], empty="."):
    class ConsolePlayer(Player):
        def __init__(self, game):
            self.game = game
            self.stones = stones
            self.labels = None
            if len(self.game.dimensions) == 2:
                self.labels = [[]]
                for i in range(self.game.dimensions[1]):
                    new = str(i+1)
                    self.labels[0].append (" "*(3-len (new))+new+" ")               
                self.labels.append([4*" " + "a b c d e f g h i j k l m n o p q r s t u v w x y z"[:2*(self.game.dimensions  [0])]+"\n"])
            self.seps = ([" "*(i+1) for i in range((len(self.game.dimensions)+1)//2)] + 
                        ["\n"*(i+1) for i in range(len(self.game.dimensions)//2)] )
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
                    text += self.stones[self.game.plan[tuple(pos)]]
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
            if self.game.won == -1:
                print("DRAW")
            elif self.game.players[self.game.won] == self:
                print("YOU WIN")
            else:
                print("YOU LOSE")
        
        def turn(self):
            self.visualize()
            while True: #just waiting for correct input
                x=self.stin(keystart="*")
                if isinstance(x,str):
                    if x in tuple("bzu"): #undo
                        self.game.undo()
                        while type(self.game.players[self.game.player_index]) != type(self):
                            self.game.undo()
                        return
                    if x in tuple("eqx"): #quit game
                        self.game.end()
                        return
                        #fails if you try to undo after that (game.wonplace = None)
                elif self.play(x):
                    return

        def choose(self):
            self.visualize()
            while True:
                x = input("/".join(self.stones)+" ")
                if x in self.stones:
                    return self.stones.index(x)
            

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
                while i < len(text): #searching for letters and numbers
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
    return ConsolePlayer

if __name__ == "__main__":
    while True:
        rules = normal if input("without swap? ") else swap
        players = [Bot, console_player()]
        if input("begin? "):
            players = players [::-1]
        p = Gomoku(players=players, rules=rules, dimensions=[15,15], win_length=5)
        p.run()
