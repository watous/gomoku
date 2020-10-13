import random

class Player:
    """Base class for all gomoku players, both human players and bots."""
    def __init__(self, game):
        self.game = game

    def play(self, position):
        #Don't touch!
        """Try to place a stone to `position`, return False if you have to try again, True otherwise."""
        return self.game.play(position, self)

    __repr__ = __str__ = lambda self : "player " + self.__class__.__name__

    def view(self):
        """Called whenever a new stone has been placed on the board.

Its position is stored in self.game.history[-1].
Index of the player who placed is stored in self.player_index.
"""
    
    def review(self, position, player_index):
        """Called when game's `undo` method is called.

Stone in `position` originally played by player with `player_index` has been removed."""
    
    def turn(self):
        """Called when your turn begins. Invoke the `play` method here."""

    #2 methods for swap rule:
    def swap(self):
        """Called before your swap: prepare, your next three turns will be swap."""

    def choose(self):
        """Called after opponent's swap: return the index of the player whose symbol you want to play with."""
        return random.randint(0, len(self.game.players)-1)

    def game_over(self):
        """Called when game is over."""

class Spectator:
    """Spectators have some of the `Player` methods.
Unlike players, they can be added and removed during the game.
"""
    def view(self):
        pass
    
    def review(self, position, player_index):
        pass

    def game_over(self):
        pass
    

    


