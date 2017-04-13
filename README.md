# RetPro

A "handheld console" with clones of some legendary, classic games. WARNING - This was my first actual finished project with Python. The commenting is terrible and I fear taking a look at the code. Someday I might clean it up, but for now it's here only for historical purposes.

- [Pong](#pong)
- [Breakout](#breakout)
- [Invaders](#invaders)


### Requirements (Windows)

- [Python 3.3.5](https://www.python.org/downloads/release/python-335/) (latest version of pygame is for 3.3.x)
- [Pygame 1.9.2](https://bitbucket.org/pygame/pygame/downloads)

Install them in the above order and you're good to go. Various Linux distros should have these available via whatever package manager they use, although the game hasn't actually been tested on any.


### Starting/Playing

Launch **RetPro.py**, and you should see something like this:

![TITLE](/images/main.png)

Now drag one of the games from the right side to the slot on top of the console, and press the play-button on the top-left corner of the console to boot it up. You can also freely drag the console itself around the screen. The stop-button next to the play-button ends & "throws" the game out of the console. Various info is printed to the command-line window when anything of value happens in-game.


#### Pong

In singleplayer/impossible mode, you move the paddle on the left side with the arrow keys. In multiplayer, the arrow keys move the right side paddle instead, while W & S control the left side. Release the ball with spacebar. The ball speed is multiplied by 1.1 for each successful hit. First to four wins. The impossible mode isn't actually impossible, it is quite possible to win it.. in theory. Quit the game anytime (return to menu) by pressing Escape.

#### Breakout

First time you start the game, only the first level (0) should be unlocked. Beat it to open the next one. In the menu, pressing "highscores" will print them to the command-line window. In-game, you move the paddle with the mouse, and release the ball with Mouse 2. Destroy all the bricks to pass on to the next level. Lose the three lives and you're thrown back to the menu. You may also get various bonuses/curses anytime you break a brick. Also, the levels may or may not be actually finished, if you want to edit them yourself, you can find them in ./games/breakout/levels/ (they're self-explanatory .txt files).

#### Invaders

Arguably the most fun game of them all. Choose a difficulty and start shooting. Arrow keys move the spaceship, shoot with spacebar. Shoot all the alien ships to get more alien ships. Each time you get them all the game speed exponentially increases. You have varying amounts of "safety walls", depending on the difficulty. Again, pressing the highscores-button in the main menu (where you can retreat anytime with Escape) will print them to the command-line window. Similar to Breakout, for each alien ship you destroy, you have a chance of getting various bonuses.


### Shoutouts

- [Bfxr](http://www.bfxr.net/) ([GitHub](https://github.com/increpare/bfxr)) - An awesome little tool to make simple sound effects for games. 
