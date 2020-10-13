
### To create your own computer player:

- Create a child class of `Player` from `player.py`.
- Look in `player.py` for comments on methods of `Player`.
- Redefine the `view` method if your player needs to calculate something after each new stone placed.
  - If you do it, then eventually redefine the `review` method to support undoing.
- **Redefine the `turn` method.** This the only one that is really neccessary.
  - Choose a position in which you want to place a stone using your algorithm.
  - Pass the position to `self.play`, if you get `True`, return,
    if you get `False`, then it's impossible to place a stone to the chosen position
    for some reason and you need to try again.
  - You can use these attributes of `self.game`:
    - `self.game.dimensions` is a tuple of gameboard sizes by axis. So for the standard 2-dimensional
    board, it is basically (width, height).
    - `self.game.win_length` is how long row of your stones you need to win.
    Longer rows win only if `self.game.freestyle` is `True`.
    - `self.game.plan` is a dictionary containing all occupied positions as keys and
    for each position the index of the player to whom it belongs. 
    - `self.game.player_index` is your player index in your turn.
    Note that it is changing during and immediately after swap.
- Redefine `swap` and `choose` methods if you want. Otherwise your player won't be aware
    of playing swap and will choose randomly.
- In `tk_app.py`, import your player, add it to `bots` and run.
    Select it in settings (rightclick), play and debug.
