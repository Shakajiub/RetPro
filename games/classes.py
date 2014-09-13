#!usr/bin/env python3

# Version 1.0.5 13.9.2014
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

import pygame, sys, os
from pygame.locals import *

#Show additional info and possible errors in the shell:
DEBUG = False

#A function to drag the console and games around the screen:
def dragNdrop(self, console, OBJECTS):
    mouse_pos = pygame.mouse.get_pos()
    mouse_press = pygame.mouse.get_pressed()[0]

    #If dragging, center self on the mouse:
    if self.dragging: self.rect.center = mouse_pos

    #Check if the mouse is inside our rect and is pressed:
    if ((self.rect.left < mouse_pos[0] < self.rect.right) and
        (self.rect.top < mouse_pos[1] < self.rect.bottom) and
        mouse_press and self.can_pick_up):

        #Move the dragged game to the end of the list of games, so that
        #it will be drawn last to the screen, above everything else:
        if self != console:
            OBJECTS.insert(3, OBJECTS.pop(OBJECTS.index(self)))

        #Drag the game, disallow anything else to be dragged:
        self.dragging = True
        for obj in OBJECTS:
            obj.can_pick_up = False
        self.can_pick_up = True

        #Keep the console/game inside the screen:
        if self == console:
            if self.rect.top < 120: self.rect.top = 120
        else:
            if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > 600: self.rect.bottom = 600
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > 800: self.rect.right = 800

    #If the mouse is NOT pressed:
    elif not mouse_press:
        for obj in OBJECTS:
            obj.dragging = False
            obj.can_pick_up = True

#Load an image and return a scaled (default = x3) surface:
def load_image(file, scale=3, tiles=False, game=False):
    
    if DEBUG and not tiles: print("[DEBUG] - Loading image '{}'".format(file))

    #Try to load & return the image:
    try:
        raw_img = pygame.image.load(os.path.join("images",file))
        width_new = pygame.Surface.get_width(raw_img) * scale
        height_new = pygame.Surface.get_height(raw_img) * scale
        return pygame.transform.scale(raw_img, (width_new, height_new))

    #If the file is gone, invalid, or something else, use
    #default image (if it's a game image) or quit to desktop:
    except pygame.error:
        if game:
            print("\n[ERROR] - Failed to load game image '{}', using default!\n".format(file))
            return "game_image_error"
        else:
            print("[ERROR] - Failed to load image '{}', aborting!".format(file))
            pygame.quit(); sys.exit()

#Replace certain RGB colors of a surface with another one:
def replace_color(surface, olds, new):

    #Get the surface width & height:
    img_width = pygame.Surface.get_width(surface)
    img_height = pygame.Surface.get_height(surface)

    #Go through each pixel:
    for horiz in range(img_width):
        for verti in range(img_height):

            #Replace old colors with the new ones:
            if surface.get_at((horiz, verti)) in olds:
                surface.set_at((horiz, verti), new)

    #Return the recolored surface:
    return surface

#Load a sound file, return silence if not pygame.mixer:
def load_sound(file):
    
    if DEBUG: print("[DEBUG] - Loading sound '{}'".format(file))
    sound_raw = os.path.join("sounds", file)

    class Silence():
        def play(self): pass

    if not pygame.mixer: return Silence()
    sound = pygame.mixer.Sound(sound_raw)
    return sound

#Load a tileset with custom tile sizes, return as a list of lists:
def load_tiles(file, width, height):
    
    if DEBUG: print("[DEBUG] - Loading tileset '{}'".format(file))
    raw_image = load_image(file, tiles=True)
    img_width, img_height = raw_image.get_size()
    width, height = width*3, height*3

    #Count the amount of tiles by dividing the image width/height by the
    #given tile width/height, append parts of the image to the list of lists:
    tileset = []
    for tile_x_pos in range(0, int(img_width / width)):
        line = []
        tileset.append(line)
        for tile_y_pos in range(0, int(img_height / height)):
            rect = (tile_x_pos * width, tile_y_pos * height, width, height)
            line.append(raw_image.subsurface(rect))
            
    return tileset

    #The tiles are now easily accessed, "tileset_name[4][2]"
    #would be the on 5th column and the 3rd row in the tileset

class New_Console():
    def __init__(self, x, y,image):

        #Set up the image & rect:
        self.image = image
        self.rect = self.image.get_rect()
        self.rect[0], self.rect[1] = x, y

        #And some booleans:
        self.ON = False
        self.locked = False
        self.dragging = False
        self.can_pick_up = True

    #Can't drag the console while it's ON or locked:
    def update(self, *args):
        if self.ON or self.locked:
            self.dragging = False
            self.can_pick_up = False

    #The shared function of all the draggable boxes:
    dragNdrop = dragNdrop

class New_Game():
    def __init__(self, x, y, image):

        #Set up the rect and the image:
        if image == "game_image_error":
            self.image = load_image("game_blank.png")
        else: self.image = image
        self.rect = self.image.get_rect()
        self.rect[0], self.rect[1] = x, y

        #And some booleans:
        self.ON = False
        self.locked = False
        self.dragging = False
        self.can_pick_up = True

    def update(self,console,GAMES):

        #If self is locked, make sure it can't be dragged:
        if self.locked:
            self.dragging = False
            self.can_pick_up = False
            
        #If self is "ON", set the position to look like it's in the console:
        if self.ON:
            self.rect.center = (console.rect.center[0], console.rect.center[1]-152)

    #And here's the shared dragging function:
    dragNdrop = dragNdrop

class New_Button():
    def __init__(self, action, x, y, images,console):

        #The action of the button, the coordinates and images:
        self.action = action
        self.x, self.y = x, y
        self.images = images
        
        #The width, height and rect:
        self.width = pygame.Surface.get_width(self.images[0])
        self.height = pygame.Surface.get_height(self.images[0])
        
        self.rect = pygame.Rect(console.rect.left + self.x, console.rect.top + self.y, self.width, self.height)

        #And again, a couple of bools:
        self.hovered = False
        self.pressed = False

    def update(self, console, OBJECTS, GAMES, GAME_MODULES, BUTTONS, screen):

        #Update the rect:
        self.rect = pygame.Rect(console.rect.left + self.x, console.rect.top + self.y, self.width, self.height)

        #Set the correct image according to the mouse pos/press:
        if not self.hovered and not self.pressed:
            self.image = self.images[0]
        elif self.hovered and not self.pressed:
            self.image = self.images[1]
        elif self.hovered and self.pressed:
            self.image = self.images[2]

        #Check the mouse position/left click:
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]

        #If the mouse is inside the button's rect:
        if ((self.rect.left < mouse_pos[0] < self.rect.right) and (self.rect.top < mouse_pos[1] < self.rect.bottom)):

            #Console can't be dragged, self is hovered:
            console.locked = True
            self.hovered = True

            #If the mouse is pressed:
            if mouse_press:
                self.pressed = True

                #If the button's action is "start":
                if self.action == "start":

                    #Go through all the games and the console:
                    for game in GAMES:

                        #If the console is already on, return:
                        if console.ON: return

                        #Otherwise, if a game is near the top center of the
                        #console, turn it on, lock it and boot up the console:
                        if game.rect.collidepoint(console.rect.center[0], console.rect.top):
                            game.ON = True
                            console.ON = True
                            game.locked = True
                        else: game.ON = False

                        #If a game has been started, load it up:
                        if game.ON: GAME_MODULES[GAMES.index(game)].load_game(console)

                #Or if the button's action is "stop":
                elif self.action == "stop":

                    #Turn off the game that is on and push it out the console:
                    for game in GAMES:
                        if game.ON:
                            game.ON = False
                            console.ON = False
                            game.rect.top -= 60

            #If the mouse isn't even pressed:
            else: self.pressed = False

        #Or hovered over:
        else:
            self.hovered = False
            self.pressed = False

            #Go through all the objects:
            for obj in OBJECTS:

                #If any buttons are hovered over, return:
                for btn in BUTTONS:
                    if btn.hovered: return

                #Otherwise, check if the object isn't "on", and unlock it:
                obj.locked = False if not obj.ON else True

class New_Display():
    def __init__(self, console):

        #Make a rect of the area in the console used to run the game in:
        self.x = console.rect.left + 84
        self.y = console.rect.top + 96
        self.rect = pygame.Rect(self.x, self.y, 231, 171)
