#!usr/bin/env python3

# Version 1.0.7 25.2.2014
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

# Version Changes (rest in "./changes/pong.txt"):

# 1.0.7 - Reorganized the code.
# 1.0.7 - Redesigned the AI. It now sticks to the vertical center of
# the board, allowing it to react to the ball better. IMPOSSIBLE AI IS SCARY.

import pygame
from pygame.locals import *
from random import randrange
from math import radians, sin, cos
from .classes import *

#Show additional info and possible errors in the shell:
DEBUG = False

#Check if sounds are available:
if not pygame.mixer:
    if DEBUG: print("\n[DEBUG] - Sounds are disabled!\n")
    SOUNDS = False
else: SOUNDS = True

#Set up the colors:
WHITE = (255,255,255)
L_GRAY = (195,195,195)
D_GRAY = (140,140,140)

class New_Paddle(pygame.sprite.Sprite):
    
    def __init__(self,control,x,y,speed,score_pos):
        pygame.sprite.Sprite.__init__(self)

        #Set up own width, height and image:
        self.width, self.height = 9, 31
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE)

        #Who controls the Paddle?:
        self.control = control

        #Set the positions (of the rect and the score), the speed and score:
        self.x, self.y, self.speed = x, y, speed
        self.score_pos, self.score = score_pos, 0
        self.rect = pygame.Rect(screen.rect.left + self.x,
                                screen.rect.top + self.y,
                                self.width, self.height)
    def update(self):

        #Get the correct movement/keys/speed according to the game mode:
        keys = pygame.key.get_pressed()

        #Get the horizontal direction of the ball:
        dir_radians = radians(OBJECTS[2].direction)
        horizontal_dir = cos(dir_radians)
        
        #Normal Single Player mode:
        if game_mode == "single":
            if self.control == "player":
                if keys[K_UP]: self.rect.top -= self.speed
                if keys[K_DOWN]: self.rect.bottom += self.speed
            elif self.control == "ai":
                for i in range(2):
                    if horizontal_dir > 0:
                        if OBJECTS[2].rect.center[1] < self.rect.center[1]:
                            self.rect.top -= 1
                        elif OBJECTS[2].rect.center[1] > self.rect.center[1]:
                            self.rect.bottom += 1
                    else:
                        if self.rect.center[1] < screen.rect.center[1]:
                            self.rect.bottom += 1
                        elif self.rect.center[1] > screen.rect.center[1]:
                            self.rect.top -= 1
                        
        #Normal Multiplayer mode:
        elif game_mode == "multi":
            if self.control == "player":
                if keys[K_w]: self.rect.top -= self.speed
                if keys[K_s]: self.rect.bottom += self.speed
            elif self.control == "ai":
                if keys[K_UP]: self.rect.top -= self.speed
                if keys[K_DOWN]: self.rect.bottom += self.speed
        
        #Impossible Single Player mode:
        if game_mode == "impossible":
            if self.control == "player":
                if keys[K_UP]: self.rect.top -= self.speed
                if keys[K_DOWN]: self.rect.bottom += self.speed
            elif self.control == "ai":
                #The LITERALLY "impossible" ai:
                #self.rect.top = ball.rect.center[1] - self.height/2+1
                for i in range(4):
                    if horizontal_dir > 0:
                        if OBJECTS[2].rect.center[1] < self.rect.center[1]:
                            self.rect.top -= 1
                        elif OBJECTS[2].rect.center[1] > self.rect.center[1]:
                            self.rect.bottom += 1
                    else:
                        if self.rect.center[1] < screen.rect.center[1]:
                            self.rect.bottom += 1
                        elif self.rect.center[1] > screen.rect.center[1]:
                            self.rect.top -= 1

        #Release the Ball with spacebar:
        if keys[K_SPACE] and OBJECTS[2].speed == 0:
            OBJECTS[2].speed = 1

        #Keep the Paddles inside the game screen:
        if self.rect.top < screen.rect.top:
            self.rect.top = screen.rect.top
        if self.rect.bottom > screen.rect.bottom:
            self.rect.bottom = screen.rect.bottom

class New_Ball(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        #Set up the width, height, speed and direction:
        self.width, self.height = 9, 9
        self.speed, self.direction = 0, 0

        #Set own position (and rect):
        self.x = screen.rect.center[0]-(self.width/2)+1
        self.y = screen.rect.center[1]-(self.height/2)+1
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        #And set the image:
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE)
        
    def update(self):

        #Move the Ball to the right direction:
        dir_radians = radians(self.direction)
        self.x += self.speed * cos(dir_radians)
        self.y -= self.speed * sin(dir_radians)
        self.rect.x = self.x
        self.rect.y = self.y

        #Add score to the correct Paddle when hitting the left or right edge:
        if self.rect.left < screen.rect.left:
            self.add_score(OBJECTS[1], OBJECTS[0])
        if self.rect.right > screen.rect.right:
            self.add_score(OBJECTS[0], OBJECTS[1])

        #Bounce from the top of the screen:
        if self.rect.top < screen.rect.top:
            if SOUNDS: bounce.play()

            #Check the direction of the Ball, bounce if going up:
            dir_radians = radians(self.direction)
            if sin(dir_radians) > 0:
                self.direction = (360-self.direction)%360
                self.rect.top = screen.rect.top + 1
                self.y = self.rect.y

        #And from the bottom of the screen:
        if self.rect.bottom > screen.rect.bottom:
            if SOUNDS: bounce.play()

            #Check the direction of the Ball, bounce if going down:
            dir_radians = radians(self.direction)
            if sin(dir_radians) < 0:
                self.direction = (360-self.direction)%360
                self.rect.bottom = screen.rect.bottom - 1
                self.y = self.rect.y
            
    def add_score(self,boardW,boardL):
        global game_mode

        #Set the correct Player names to be displayed on the shell:
        if boardW == OBJECTS[0]:
            bW, bL = "Player", "AI"
            if game_mode == "multi": bW, bL = "Player 1", "Player 2"
        elif boardW == OBJECTS[1]:
            bW, bL = "AI", "Player"
            if game_mode == "multi": bW, bL = "Player 2", "Player 1"

        #Add score (if it's less than three) and print it:
        if boardW.score < 3:
            print("\nPoint for the {}! The {} starts.\n".format(bW,bL))
            print("Press [Space] to release the Ball!\n")
            boardW.score += 1

        #Or restart the game (if it's the fourth point):
        else:
            if boardL.score != 0:
                print("\nThe {} wins! ({}:{})\n".format(bW,boardW.score+1,boardL.score))
            else: print("\nA PERFECT victory for the {}! (4:0)\n".format(bW))
            boardW.score, boardL.score = 0, 0
            game_mode = "menu"
            
        self.reset(boardL)

    def bounce(self,diff,board):
        
        if SOUNDS: bounce.play()

        #Reverse the horizontal direction, add some angle:
        self.direction = (180-self.direction)%360
        self.direction += diff*3 if board == OBJECTS[0] else -diff*3

        #Don't get stuck inside the Paddles:
        dir_radians = radians(self.direction)
        if ((self.speed * cos(dir_radians) < 0 and board == OBJECTS[0]) or
            (self.speed * cos(dir_radians) > 0 and board == OBJECTS[1])):
            self.direction = (180-self.direction)%360

        #Print and possibly update the speed of the Ball:
        if self.speed < 8.5:
            self.speed *= 1.1
            print("Ball speed: {}".format(self.speed))
        else: print("Ball speed: MAXIMUM!!!")

        #The Ball speed CAN'T be more than 9,
        #or it could just jump over the Paddles:
        if self.speed > 9: self.speed = 8.9

    def reset(self,starter=None):

        #Reset the positions of the Paddles and the Ball:
        self.x = screen.rect.center[0]-(self.width/2)+1
        self.y = screen.rect.center[1]-(self.height/2)+1
        self.rect.x, self.rect.y = self.x, self.y
        
        OBJECTS[0].x, OBJECTS[0].y = 3, 70
        OBJECTS[1].x, OBJECTS[1].y = 219, 70
        
        OBJECTS[0].rect = pygame.Rect(screen.rect.left + OBJECTS[0].x,
                                      screen.rect.top + OBJECTS[0].y,
                                      OBJECTS[0].width, OBJECTS[0].height)
        
        OBJECTS[1].rect = pygame.Rect(screen.rect.left + OBJECTS[1].x,
                                      screen.rect.top + OBJECTS[1].y,
                                      OBJECTS[1].width, OBJECTS[1].height)

        #Reset own speed and blast off towards either Paddle:
        self.speed, self.direction = 0, randrange(-45,45)
        if starter == OBJECTS[0]: self.direction += 180
        elif starter == None:
            if randrange(2): self.direction += 180

class New_Mode_Select():
    
    def __init__(self,image,x,y,name,key):

        #The name and key (in the keyboard) of the button:
        self.name, self.key = name, key

        #Set up the image and a timer:
        self.original_image = image
        self.image = self.original_image
        self.timer = 0

        #Some booleans:
        self.hovered = False
        self.pressed = False
        self.enabled = True

        #Finally, set up the rect:
        self.width = pygame.Surface.get_width(self.image)
        self.height = pygame.Surface.get_height(self.image)
        self.rect = pygame.Rect(screen.rect.left + x,
                                screen.rect.top + y,
                                self.width, self.height)
    def update(self):
        global game_mode

        #Set the correct image color if hovered over with the mouse:
        if self.hovered and self.enabled:
            self.image = self.original_image.copy()
            replace_color(self.image, [WHITE], L_GRAY)
        elif not self.enabled:
            self.image = self.original_image.copy()
            replace_color(self.image, [WHITE, L_GRAY], D_GRAY)
        else: self.image = self.original_image

        #Control the timer:
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.enabled = True

        #Check for mouse position or mouse or keyboard press:
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]
        key_press = pygame.key.get_pressed()

        #Set the game mode if self pressed (and self enabled):
        if (self.pressed and self.hovered) or key_press[self.key]:
            if self.enabled:

                #Disable the button for a second:
                self.timer = 30
                self.enabled = False

                #Start up the game:
                game_mode = self.name
                print("Press [Space] to release the Ball!\n")

        #Check if the button is hovered over or pressed:
        if ((self.rect.left < mouse_pos[0] < self.rect.right) and
            (self.rect.top < mouse_pos[1] < self.rect.bottom)):
            self.hovered = True
            
            if mouse_press: self.pressed = True
            else: self.pressed = False
            
        else: self.hovered, self.pressed = False, False
    
def init(x,y):

    #Initialize the game, make the draggable box in the main window:
    return New_Game(x,y,load_image("game_pong.png",game=True))

def load_sounds():
    global bounce, button

    #Load all the sounds used:
    bounce = load_sound("general_bounce.ogg")
    button = load_sound("general_button.ogg")

def load_game(console):
    global screen, NUMS, BKG, OBJECTS, BALLS, BUTTONS, game_mode
    
    #Set up various game objects and lists:
    
    game_mode = "menu"
    screen = New_Display(console)

    #The Paddles and their scores' display positions:
    player_score_pos = (screen.rect.center[0]-27,screen.rect.top+12)
    ai_score_pos = (screen.rect.center[0]+16,screen.rect.top+12)
    player = New_Paddle("player", 3, 70, 3, player_score_pos)
    ai = New_Paddle("ai", 219, 70, 3, ai_score_pos)

    #Mode selection buttons:
    if DEBUG: print("")
    btn_imgs = load_tiles("pong_buttons.png",55,5)
    btn_singl = New_Mode_Select(btn_imgs[0][0],21,81,"single",K_s)
    btn_multi = New_Mode_Select(btn_imgs[0][1],21,101,"multi",K_m)
    btn_impos = New_Mode_Select(btn_imgs[0][2],21,135,"impossible",K_i)
    BUTTONS = [btn_singl, btn_multi, btn_impos]

    #The initial Ball:
    ball = New_Ball()
    BALLS = pygame.sprite.Group()
    BALLS.add(ball)
    
    OBJECTS = [player, ai, ball]
    ball.reset()

    #Load the numbers (0-9) as a tileset:
    NUMS = load_tiles("font_numbers.png",4,5)

    #Self-explanatory:
    if SOUNDS: load_sounds()

    #Finally, load the backgrounds (menu and the main game):
    BKG = []
    for img in ["pong_bkg.png","pong_menu.png"]:
        BKG.append(load_image(img))
    if DEBUG: print("")
    
    print("\nLoaded Pong!\n")

def main(display):
    global game_mode

    #Make the code below a bit more readable:
    player, ai, ball = OBJECTS[0], OBJECTS[1], OBJECTS[2]

    #Return to the menu if Escape pressed:
    keys = pygame.key.get_pressed()
    if keys[K_ESCAPE]:
        ball.reset()
        player.score, ai.score = 0, 0
        game_mode = "menu"

    #Draw the menu, if in it:
    if game_mode == "menu":
        display.blit(BKG[1], screen.rect)
        for mode in BUTTONS:
            mode.update()
            display.blit(mode.image, mode.rect)
        return

    display.blit(BKG[0], screen.rect)
    for obj in OBJECTS:
        
        #Go through each object, update and blit them:
        obj.update()
        display.blit(obj.image, obj.rect)

        #Blit the Players' scores:
        if obj in [player, ai]:
            display.blit(NUMS[obj.score][0], obj.score_pos)

            #And check if collided with the Ball:
            if pygame.sprite.spritecollide(obj,BALLS,False):
                diff = (obj.rect.center[1]) - (ball.rect.center[1])
                if obj == player:
                    ball.rect.left = player.rect.right
                elif obj == ai:
                    ball.rect.right = ai.rect.left
                ball.bounce(diff,obj)
