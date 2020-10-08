from functools import reduce
#from time import sleep
import warnings

## OPTIONS FOR RULES
"""These functions are passed to the rules attribute of Gomoku class.
They take the Gomoku instance as an argument and return a function which
takes turn index as an argument and returns the index of the player on turn.
"""

def normal(game):
    def action(turn):
        return turn % len(game.players)
    return action

def swap(game):
    def action(turn):
        if turn == 0:
            game.players[0].swap()
        elif turn in (1,2):
            game.players = game.players[::-1]
        elif turn == 3:
            if 1 != game.players[1].choose():
                game.players = game.players[::-1]
        return turn % len(game.players)
    return action

rules_options = [normal, swap]

## MAIN CLASS

class Gomoku:
    def __init__(self,
                 players=[],
                 dimensions=(15,15),
                 winlength=5,
                 rules=normal,
                 spectators=[],
                 ):
        """Class to run a gomoku game

Args:
    players: list of player classes in order (they should be subclasses of `Player`)
    dimensions (tuple): size of plan by axis
    winlength: number of symbols in a row to win
    rules: one of rules functions   
"""
        self.dimensions = dimensions
        self.size = reduce(lambda x,y:x*y, self.dimensions)

        self.winlength = winlength

        self.players = [p(self) for p in players]

        self.rules = rules(self)


        self.spectators = [s(self) for s in spectators]
        
        self.plan = {} #souřadnice: číslo hráče
        self.history = [] #souřadnice
        self.win = None #None: hra v průběhu, -1: remíza, jinak: číslo vyhrávajícího hráče
        self.winplace = None #[začátek výherní ntice, konec výherní ntice] (souřadnice)


    def run(self):
        while self.win is None:
            self.played = False
            #self.rules(len(self.history))
            
            self.player_index = self.rules(len(self.history))
            if not -len(self.players) <= self.player_index < len(self.players):
                raise IndexError("player index out of range")
            player = self.players[self.player_index]
            player.turn()
            if (not self.played) and player == self.players[self.player_index]:
                raise Exception #wait until played

        for p in self.players:
            p.game_over()
        for s in self.spectators:
            s.game_over()
        return

    def isempty(self, pos):
        if pos in self.plan or len(pos) != len(self.dimensions):
            return False
        for p,d in zip(pos, self.dimensions):
            if not 0 <= p < d:
                return False
        return True
        
    def play(self, pos, player=None):
        """return False on invalid move attempt, True otherwise"""
        if self.win is not None or player != self.players[self.player_index]:
            #warnings.warn("{} tried to play out of their turn".format(player))
            return True
        if not self.isempty(pos):
            #warnings.warn("{} tried to make an invalid move to {}".format(player, pos))
            return False

        self.history.append(pos)
        self.plan[pos] = self.player_index
        #zacatek overovani vyhry
        lend = len(self.dimensions)
        step = [-1 for _ in range(lend)]
        pos = list(pos)
        current = pos[:]
        while step != [0 for _ in range (lend)]:
            ends = []
            row = -1
            for drc in (-1,1):
                ends.append(tuple(pos))
                while self.plan.get(tuple(pos),None) == self.player_index:
                    ends[-1] = tuple(pos)
                    row += 1
                    for i in range(lend):
                        try:
                            pos[i] += drc * step[i]
                        except IndexError:
                            raise IndexError("pos had only {} dimensions({} needed)".format(len(pos),len(self.dimensions)))
                pos = current[:]
            if row == self.winlength:
                self.win = self.player_index
                self.winplace = ends
                break
            i = 0
            while i < lend and step[i] == 1:
                step[i] = -1
                i += 1
            step[i] += 1
        if len(self.plan) >= self.size:
            self.win = -1 #remíza
        #konec overovani vyhry
        self.played = True
        for p in self.players:
            p.view()
        for s in self.spectators:
            s.view()
        return True

    def undo(self, repeat=1):
        for i in range(repeat):
            if not self.history:
                break
            pos = self.history.pop()
            self.player_index = self.plan[pos]
            del self.plan[pos]
            for p in self.players:
                p.review(pos, self.player_index)
            for s in self.spectators:
                s.review(pos, self.player_index)
        if self.win is not None:
            self.win = None
            self.winplace = None
            self.run()
        return

    def destroy(self):
        self.win = -1
        self.players = self.spectators = []
        self.played = True

    '''
    def totext(self, name=None):
        text = ["#piskvorky.py hra"]
        if name is not None:
            text.append(": " + name)
        text.append("\n")
        text.append(",".join(map(str, self.dimensions)))
        text.append(" " + str(self.winlength) + "\n")
        for p in self.history:
            text.append(" ".join(",".join(map(str, p))))
            text.append(";" + str(self.plan[p]) + "\n")
        if self.win:
            text.append("\n" + self.win + " " + ",".join(map(str,self.winplace[0])) + " " + ",".join(map(str,self.winplace[1])))
        return "".join(text)

    #udělat:
    def fromtext(text, *args, **kwargs):
        """game.fromtext(Obj.totext()) -> Obj
*args and **kwargs will be passed to the object."""
        i = 0
        for line in text.split("\n"):
            if line[0]=="#":
                continue
            elif i == 0:
                line = line.split()
                new = Gomoku(dimensions=tuple(map(int, line[0].split(","))), winlength=int(line[1]), *args, **kwargs)
            elif i == 1:
                line = line.split()
                for word in line:
                    pos,_,player_index = word.partition(";")
                    pos = tuple(map(int, pos.split(","))) 
            elif i == 2:
                line = line.split()
                new.win = line[0]
                new.winplace = (tuple(map(int, line[1].split(","))), tuple(map(int, line[2].split(","))))
            i += 1
        return new
    '''

    def __str__(self):
        return str(self.__dict__)

    def __contains__(self,pos):
        return pos in self.plan

if __name__ == "__main__":
    from player import Player
    from megabot import Megabot
    
    class Basic(Player):
        def view(self):
            print(self.game.player_index, self.game.history[-1])
        def turn(self):
            res = False
            while not res:
                try:
                    x = input("    "+str(self.game.player_index)+" > ")
                    res = self.play(tuple(map(int,x.split(","))))
                except Exception as e:
                    print(e)
        def game_over(self):
            print(self.game.win)

    p = Gomoku (dimensions=[15,15], winlength=5, players=[Basic, Megabot])
    print("enter coordinates separated by commas")
    p.run()
