from functools import reduce
import weakref
#import warnings

## OPTIONS OF RULES
#These functions are passed to the rules attribute of Gomoku class.
#They take the Gomoku instance as an argument and return a function which
#takes turn index as an argument and returns the index of the player on turn.

def normal(game):
    def action(turn):
        return turn % len(game.players)
    return action

def swap(game): #for 2 players only
    def action(turn):
        if turn == 0:
            game.players[0].swap()
        elif turn in (1,2):
            game.players.reverse()
        elif turn == 3:
            if 1 != game.players[1].choose():
                game.players.reverse()
        return turn % len(game.players)
    return action

#add rules here
rule_options = [normal, swap]

## MAIN CLASS

class Gomoku:
    """class running a gomoku game"""
    def __init__(self,
                 players=[],
                 dimensions=(15,15),
                 win_length=5,
                 rules=normal,
                 freestyle=False,
                 spectators=[],
                 ):
        """
Args:
    players: list of player classes in order (they should be subclasses of `Player`)
    dimensions (tuple of integers): size of gameboard in each direction
    win_length: number of stones in a row to win
    rules: one of rules functions
    freestyle (bool): whether rows with more than `win_length` stones win
    spectators: list of spectator objects

more on players and spectators in `player.md`

invoke `run` to start the game.
"""
        #here are some attributes useful for players and spectators:

        self.dimensions = dimensions #size of gameboard in each direction
        self.size = reduce(lambda x,y:x*y, self.dimensions)

        self.win_length = win_length #number of stones in a row to win

        self.players = [p(weakref.proxy(self)) for p in players] #

        self.rules = rules(weakref.proxy(self))
        self.freestyle = freestyle

        self.spectators = spectators
        for s in self.spectators:
            s.game = weakref.proxy(self)
        
        self.plan = {} #{position: player_index  for all occupied positions}
        self.history = [] #list of positions of stones in order of time of placing
        self.won = None #None: game in progress, -2: end forced, -1: draw (board filled), other: index of player who have won
        self.winning_row = None #if game is won by someone: [position of one end of the winning row, position of its other end]

    def run(self):
        while self.won is None:
            self.played = False #whether the player has already placed a stone in the current turn
            self.player_index = self.rules(len(self.history))
            if self.won is not None: #ending game in turn
                break
            if not -len(self.players) <= self.player_index < len(self.players):
                raise IndexError("player index out of range")
            player = self.players[self.player_index]
            player.turn()
            if (not self.played) and player == self.players[self.player_index]:
                raise Exception("{} didn't place any stone in their turn".format(self.players[self.player_index]))
                # TODO  rather than raising an exception, wait until the stone is placed
        if self.won != -2:
            for p in self.players:
                p.game_over()
            for s in self.spectators:
                s.game_over()
        return

    def is_empty(self, position):
        if position in self.plan or len(position) != len(self.dimensions):
            return False
        for p,d in zip(position, self.dimensions):
            if not 0 <= p < d:
                return False
        return True
        
    def play(self, position, player=None):
        """return False on invalid move attempt, True otherwise"""
        if self.won is not None or self.played or player != self.players[self.player_index]:
            #warnings.warn("{} tried to play out of their turn".format(player))
            return True
        if not self.is_empty(position):
            #warnings.warn("{} tried to make an invalid move to {}".format(player, position))
            return False

        self.history.append(position)
        self.plan[position] = self.player_index
        #checking for winning rows begins
        lend = len(self.dimensions)
        step = [-1 for _ in range(lend)]
        position = list(position)
        current = position[:]
        while any(step):
            ends = []
            row = -1
            for drc in (-1, 1):
                ends.append(tuple(position))
                while self.plan.get(tuple(position),None) == self.player_index:
                    ends[-1] = tuple(position)
                    row += 1
                    for i in range(lend):
                        try:
                            position[i] += drc * step[i]
                        except IndexError:
                            raise IndexError("position had only {} dimensions({} needed)".format(len(position),len(self.dimensions)))
                position = current[:]
            if row == self.win_length or (self.freestyle and row >= self.win_length):
                self.won = self.player_index
                self.winning_row = ends
                break
            i = 0
            while i < lend and step[i] == 1:
                step[i] = -1
                i += 1
            step[i] += 1
        if len(self.plan) >= self.size: #board full
            self.won = -1 #draw
        #checking for winning rows ends
        self.played = True
        for p in self.players:
            p.view()
        for s in self.spectators:
            s.view()
        return True

    def undo(self, repeat=1):
        """go back `repeat` turns"""
        for i in range(repeat):
            if not self.history:
                break
            position = self.history.pop()
            self.player_index = self.plan[position]
            del self.plan[position]
            for p in self.players:
                p.review(position, self.player_index)
            for s in self.spectators:
                s.review(position, self.player_index)
        if self.won is not None:
            self.won = None
            self.winning_row = None
            self.run()
        else:
            self.played = True
        return

    def end(self):
        """to be called if the game is to be quitted without having been finished"""
        self.won = -2
        self.played = True

    def __contains__(self, position):
        return position in self.plan



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
            print(self.game.won)

    p = Gomoku (dimensions=[15,15], win_length=5, players=[Basic, Megabot])
    print("this is the simplest input method, you most certainly want something else (tk_app.py)")
    print("enter coordinates separated by commas")
    p.run()
