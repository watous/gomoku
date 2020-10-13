# gomoku
Python imlementation of gomoku with possibility to add own computer players.

**To play:** download and run `tk_app.py`, no external packages are neccessary.
 - click to play
 - press <kbd>Ctrl</kbd>+<kbd>Z</kbd> to undo a move
 - when game's over, click to start a new game
 - rightclick to open settings
    - in settings you can control players (computer/human), appearance, opening rule, size of the board and length of winning row
    - if you select more than one option from players,
      random selected option will be used for each game

If you can't run `tk_app.py` for any reason, use `console_player.py`.

See instructions on how to create a custom computer player in `player.md`. It is also possible to define your own design of board and stones on tkinter canvas, define your own opening rule,
play in more (or less) than 2 players and play in more (or less) than 2 dimensions (not in the GUI, though). Search in the files for that.

