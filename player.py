import random

class Player:
    """Base class for all gomoku players, both human and computer."""
    def __init__(self, game):
        self.game = game

    def play(self, pos):
        #don't touch
        return self.game.play(pos, self)

    def __str__(self):
        return "player " + self.__class__.__name__
    __repr__ = __str__

    def view(self):
        """New symbol has been placed on the plan (it might be yours).
It is in position self.game.history[-1] and from player number self.game.plan[self.game.history[-1]]."""
        pass
    
    def review(self, pos, player):
        """Symbol in position pos from player has been removed by undo()."""
        pass
    
    def turn(self):
        """Your turn."""
        pass

    def choose(self):
        """After swap: return the index of the player whose symbol you want to play with."""
        return random.randint(0, len(self.game.players)-1)

    def swap(self):
        """Prepare, your next three turns will be swap."""
        pass

    def game_over(self):
        """Game ended."""
        pass

class Spectator:
    def __init__(self, game):
        self.game = game

    def view(self):
        pass
    
    def review(self, pos, player):
        pass

    def game_over(self):
        pass
    

    


