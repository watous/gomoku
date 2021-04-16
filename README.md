# gomoku
Python implementation of gomoku with possibility to add custom computer players (see instructions in `player.md` for that). One simple computer player is included.

**To play:** Download and run `tk_app.py`, no external packages are neccessary.
 - Click to play
 - Press <kbd>Ctrl</kbd>+<kbd>Z</kbd> to undo a move.
 - When game's over, click to start a new game.
 - Rightclick or <kbd>F10</kbd> to open settings.
    - In settings you can control players (computer/human), appearance, opening rule (none/swap), size of the board and length of winning row.
    - If you select more than one option from players,
      random selected option will be used for each game.
    - Appearance: You can switch between paper & pencil and go. If you have `PIL` installed, you can open skins (experimental) and make custom skins. For the best guide to creating skins see example skins in the skins folder.
    - Settings may take effect only after restarting game (<kbd>Enter</kbd>).

If you can't use `tk_app.py` for any reason, use `console_game.py`.

For those who want to edit code: it is also possible to define your own design of board and stones on tkinter canvas, define your own opening rule, play in more than 3 (or less than 2) players and play in more (or less) than 2 dimensions (not in the GUI, though). Search in the files for that.