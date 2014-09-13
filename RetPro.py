#!usr/bin/env python3

# Version 1.0.2 25.2.2014
# Copyright 2014 Jere Oikarinen

#    This file is part of RetPro.
#
#    RetPro is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RetPro is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RetPro.  If not, see <http://www.gnu.org/licenses/>.

import pygame, sys
import games.pong
import games.breakout
import games.invaders
from pygame.locals import *
from games.classes import *

#Show additional info and possible errors in the shell:
DEBUG = False

#Set up some colors:
L_GRAY = (195,195,195)

def main():

    #Initialize pygame and set up the important stuff:
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_icon(load_image("retpro_icon.png"))
    pygame.display.set_caption("RetPro")
    pygame.mouse.set_visible(False)

    #A clock to keep the fps stable:
    clock = pygame.time.Clock()

    #Load up the surfaces and some tilesets:
    mouse = load_image("retpro_mouse.png")
    console = load_image("retpro_console.png")
    btn_imgs = load_tiles("retpro_buttons.png",10,10)

    #Set up the main console and it's buttons:
    supah_console = New_Console(120,120,console)

    button1 = New_Button("start",12,12,[btn_imgs[0][0], btn_imgs[1][0],
                                        btn_imgs[2][0]], supah_console)
    
    button2 = New_Button("stop",51,12,[btn_imgs[0][1], btn_imgs[1][1],
                                       btn_imgs[2][1]], supah_console)
    BUTTONS = [button1, button2]

    #Lists of the games and objects:
    GAME_MODULES = [games.pong, games.breakout, games.invaders]
    OBJECTS = [supah_console]
    GAMES = []

    #Set up the initial positions of all the games:
    xpos, ypos = 550, 50
    for game in GAME_MODULES:

        #Initialize the game in the set position:
        game_obj = game.init(xpos,ypos)

        #Append the game object to the main lists:
        OBJECTS.append(game_obj)
        GAMES.append(game_obj)

        #And set up the position for the next one:
        xpos += 9; ypos += 102

    #THE MAIN "GAME" LOOP:
    while True:

        #Check the pygame events:
        for event in pygame.event.get():

            #Quit the game correctly:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            #A backup for draggable objects:
            elif event.type == MOUSEBUTTONUP:
                for obj in OBJECTS:
                    obj.dragging = False
                    obj.can_pick_up = True

        #Fill the screen light gray:
        screen.fill(L_GRAY)

        #Update and possibly drag the main objects:
        for obj in OBJECTS:
            obj.dragNdrop(supah_console, OBJECTS)
            obj.update(supah_console, GAMES)

            #Blit it if it's the console:
            if obj == supah_console:
                screen.blit(obj.image, obj.rect)

        #If a game is "on", draw it:
        for game in GAMES:
            if game.ON: GAME_MODULES[GAMES.index(game)].main(screen)

        #Update and blit the console's buttons:
        for btn in BUTTONS:
            btn.update(supah_console, OBJECTS, GAMES, GAME_MODULES, BUTTONS, screen)
            screen.blit(btn.image, btn.rect)

        #Finally, blit the draggable "games":
        for obj in OBJECTS:
            if obj != supah_console:
                screen.blit(obj.image, obj.rect)

        #Wait, one more thing, blit the mouse:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(mouse, mouse_pos)

        #And update the screen & control the fps:
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__": main()
