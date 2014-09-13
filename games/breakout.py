#!usr/bin/env python3

# Version 1.0.6 25.2.2014
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

# Version Changes (rest in "./changes/breakout.txt"):

# 1.0.6 - Reorganized the code, yet again.

import pygame
from pygame.locals import *
from random import randrange, randint
from math import radians, sin, cos
from .classes import *

#Show additional info and possible errors in the shell:
DEBUG = False

#Check if sounds are available:
if not pygame.mixer:
    if DEBUG: print("\n[DEBUG] - Sounds are disabled!\n")
    SOUNDS = False
else: SOUNDS = True

#Set up some colors:
WHITE = (255,255,255)
L_GRAY = (195,195,195)
D_GRAY = (140,140,140)

class New_Paddle(pygame.sprite.Sprite):
    
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)

        #Set up the width, height and image:
        self.width, self.height = 31, 9
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE)

        #Score, multiplier, lives and speed:
        self.score, self.multiplier = 0, 1.0
        self.lives, self.speed = 3, 3

        #Special timed bonuses:
        self.timer = 0
        self.large_board = False
        self.small_board = False
        self.time_distortion = False
        self.bonuses_enabled = True
        
        #And finally, own position and rect:
        self.x, self.y = screen.rect.left + x, screen.rect.top + y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def update(self):
        global LEVEL, BALLS, OBJECTS

        #Check for input:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        #Return to the menu with escape:
        if keys[K_ESCAPE]: reset_game(); return

        #Paddle movement:
        self.x = mouse_pos[0] - (self.width/2) + 1
        self.rect.x, self.rect.y = self.x, self.y

        #Keep the Paddle inside the screen area:
        if self.rect.left < screen.rect.left:
            self.rect.left = screen.rect.left
        if self.rect.right > screen.rect.right:
            self.rect.right = screen.rect.right

        #Count down the timer, when reached zero, remove all bonuses:
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                
                #Remove bonuses:
                self.large_board = False
                self.small_board = False
                self.time_distortion = False

                #Reset the Paddle:
                self.width, self.height = 31, 9
                self.image = pygame.Surface([self.width, self.height])
                self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
                self.image.fill(WHITE)

                #Reset the Ball(s):
                for ball in BALLS:
                    if ball.speed not in [0, 2]:
                        ball.speed = 2

        #Release the Balls with space or mouse 2, if locked:
        mouse_press = pygame.mouse.get_pressed()[2]
        for ball in BALLS:
            if (keys[K_SPACE] or mouse_press) and ball.speed == 0:
                direction, backup_dir = randrange(-5,5), randint(0,1)
                if direction == 0 and backup_dir == 0: direction = -5
                elif direction == 0 and backup_dir == 1: direction = 5
                ball.direction = -90 + direction
                ball.speed = 2

        #Check for remaining Bricks, if none exist, move to the next level.
        #Also, reset the score and remove any extra Balls in the field:
        if len(BRICKS) <= 0:
            save_scores()
            print(); LEVEL += 1
            for ball in BALLS:
                if len(BALLS) > 1:
                    for l in [OBJECTS, BALLS]: l.remove(ball)
                else: ball.reset()
            self.score, self.multiplier = 0.0, 1.0
            load_level()

    def add_score(self):
        extra_ball_bonus = False
        total_extra_bonus = 0
        
        #An extra Balls bonus; for each Ball moving(!) in the screen,
        #a bonus of three (3) is added to the multiplier:
        if len(BALLS) > 1:
            moving_balls = -1

            #Go through all the balls, add +1 to moving_balls
            #for each ball with a speed above zero:
            for ball in BALLS:
                if ball.speed != 0:
                    moving_balls += 1
                    extra_ball_bonus = True

            if extra_ball_bonus:
                self.multiplier += moving_balls*3.0
                total_extra_bonus += moving_balls*3.0

        #Small Paddle bonus; increase multiplier by 0.5:
        if self.small_board:
            self.multiplier += 0.5
            total_extra_bonus += 0.5

        #Large Paddle penalty; decrease multiplier by 0.5:
        if self.large_board:
            self.multiplier -= 0.5
            total_extra_bonus -= 0.5

        #Time distortion penalty; decrease multiplier by 0.5:
        if self.time_distortion:
            self.multiplier -= 0.5
            total_extra_bonus -= 0.5

        #Give points and print them:
        self.score += self.multiplier
        
        if self.multiplier == 1.0:
            print("Score:{:8}".format(round(self.score)))
        else:
            print("Score:{:8} | {:7}Multiplier".format(round(self.score),
                                                       str(self.multiplier)), end="")
            #If the player gets bonus points:
            if total_extra_bonus > 0: print(" [ +{} ]\n".format(total_extra_bonus), end="")
            elif total_extra_bonus < 0: print(" [ {} ]\n".format(total_extra_bonus), end="")
            else: print("\n")

        #Increase the multiplier:
        self.multiplier += 0.5

class New_Ball(pygame.sprite.Sprite):
    
    def __init__(self,reset=True):
        pygame.sprite.Sprite.__init__(self)

        #Set own width, height, speed and direction:
        self.width, self.height = 9, 9
        self.speed, self.direction = 0, 0

        #The position and the rect:
        self.x = OBJECTS[0].rect.center[0] - (self.width/2) + 1
        self.y = OBJECTS[0].rect.center[1] - (self.height/2) - 11
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        #And the image:
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE)

        if reset: self.reset()
        
    def update(self):

        #Make the code below a bit more readable:
        player = OBJECTS[0]
        
        #Move the Ball to the right direction:
        dir_radians = radians(self.direction)
        self.x += self.speed * cos(dir_radians)
        self.y -= self.speed * sin(dir_radians)
        self.rect.x = self.x
        self.rect.y = self.y

        #Keep self above the Paddle, if locked:
        if self.speed == 0:
            self.x = player.rect.center[0] - (self.width/2) + 1

        #A function to save up some space below:
        def corner_bounce(self,other,less1,less2,less3,less4,direction,
                          more1,more2,more3,more4,corner):
            
            if (((less1 < less2) and (less3 < less4)) and
                ((more1 > more2) and (more3 > more4))):

                #Set the new position of the Ball, top left corner:
                if corner == "tl":
                    self.rect.bottom = brick.rect.top + 4
                    self.rect.right = brick.rect.left - 1

                #Top right corner of the Brick:
                if corner == "tr":
                    self.rect.bottom = brick.rect.top + 4
                    self.rect.left = brick.rect.right + 1

                #Bottom left corner:
                if corner == "bl":
                    self.rect.top = brick.rect.bottom - 4
                    self.rect.right = brick.rect.left - 1

                #And the bottom right one:
                if corner == "br":
                    self.rect.top = brick.rect.bottom - 4
                    self.rect.left = brick.rect.right + 1
                    
                self.x, self.y = self.rect.x, self.rect.y
                
                if SOUNDS: SNDS[0].play()

                #Send the ball to given direction, damage the brick:
                diff = randrange(-5,5)
                self.direction = direction
                self.direction += diff
                other.get_hit()

                #If bounced from a corner:
                return True

        for brick in BRICKS:

            #If the Ball somehow ends up INSIDE a Brick, bounce
            #off from the nearest corner of the said Brick:

            #Set some temporary, shorter names:
            srt, srb = self.rect.top, self.rect.bottom
            srl, srr = self.rect.left, self.rect.right
            brt, brb = brick.rect.top, brick.rect.bottom
            brl, brr = brick.rect.left, brick.rect.right

            bounced = False
            
            #Bottom right corner:
            if corner_bounce(self, brick, srl, brr, srt, brb, -45,
                             srr, brr, srb, brb, "br"): bounced = True
            #Bottom left corner:
            if corner_bounce(self, brick, srt, brb, srl, brl, -135,
                             srr, brl, srb, brb, "bl"): bounced = True
            #Top right corner:
            if corner_bounce(self, brick, srl, brr, srt, brt, 45,
                             srb, brt, srr, brr, "tr"): bounced = True
            #And the top left one:
            if corner_bounce(self, brick, srl, brl, srt, brt, 135,
                             srb, brt, srr, brl, "tl"): bounced = True

            #Some bools to help with the Ball bouncing checks:
            collided_top, collided_bottom = False, False
            collided_left, collided_right = False, False
            brick_horizontal, brick_vertical = False, False

            #If the top of the Brick is hit, turn on the boolean:
            if ((brick.rect.top - 1 == self.rect.bottom) or
                (brick.rect.top - 2 == self.rect.bottom)):
                collided_top = True

            #Same for the bottom of the Brick:
            if ((brick.rect.bottom + 1 == self.rect.top) or
                (brick.rect.bottom + 2 == self.rect.top)):
                collided_bottom = True

            #The left side:
            if ((brick.rect.left - 1 == self.rect.right) or
                (brick.rect.left - 2 == self.rect.right)):
                collided_left = True

            #And the right one:
            if ((brick.rect.right + 1 == self.rect.left) or
                (brick.rect.right + 2 == self.rect.left)):
                collided_right = True

            #Check if the Ball is horizontally on the same level as the Brick:
            if (brick.rect.left-5 < self.rect.center[0] < brick.rect.right+5):
                brick_horizontal = True

            #Or vertically:
            if (brick.rect.top-5 < self.rect.center[1] < brick.rect.bottom+5):
                brick_vertical = True

            #If the Ball is horizontally on the area with the Brick, and
            #hits the top of it (and hasn't already bounced from a corner):
            if brick_horizontal and collided_top and not bounced:
                if SOUNDS: SNDS[0].play()

                #Check the direction the Ball is going:
                dir_radians = radians(self.direction)
                if sin(dir_radians) < 0:

                    #Bounce vertically and set the position
                    #outside the Brick to avoid hitting it twice:
                    self.direction = (360-self.direction)%360
                    self.rect.bottom = brick.rect.top - 1
                    self.y = self.rect.y

                    #Damage the Brick and add some points:
                    brick.get_hit()
                    player.add_score()

            #Same as above, but this time the bottom side of the Brick:
            if brick_horizontal and collided_bottom and not bounced:
                if SOUNDS: SNDS[0].play()

                #Check the Ball's direction:
                dir_radians = radians(self.direction)
                if sin(dir_radians) > 0:

                    #Bounce and set the position just outside the Brick:
                    self.direction = (360-self.direction)%360
                    self.rect.top = brick.rect.bottom + 1
                    self.y = self.rect.y

                    #Do the damage:
                    brick.get_hit()
                    player.add_score()

            #This one here is the left side of the Brick:
            if brick_vertical and collided_left and not bounced:
                if SOUNDS: SNDS[0].play()

                #Again, check the direction (this can change above):
                dir_radians = radians(self.direction)
                if cos(dir_radians) > 0:

                    #Bounce horizontally, set the new position:
                    self.direction = (180-self.direction)%360
                    self.rect.right = brick.rect.left - 1
                    self.x = self.rect.x

                    #Damage & Award:
                    brick.get_hit()
                    player.add_score()

            #Finally, the right side of the Brick:
            if brick_vertical and collided_right and not bounced:
                if SOUNDS: SNDS[0].play()

                #Final check of the Ball's direction:
                dir_radians = radians(self.direction)
                if cos(dir_radians) < 0:

                    #Final bounce and position set:
                    self.direction = (180-self.direction)%360
                    self.rect.left = brick.rect.right + 1
                    self.x = self.rect.x

                    #Final Brick damage & score addition:
                    brick.get_hit()
                    player.add_score()

        #Bounce from the top of the screen:
        if self.rect.top < screen.rect.top:
            if SOUNDS: SNDS[0].play()

            #Check the direction of the Ball, bounce it if going up:
            dir_radians = radians(self.direction)
            if sin(dir_radians) > 0:
                self.direction = (360-self.direction)%360
                self.rect.top = screen.rect.top + 1
                self.y = self.rect.y

        #The left edge of the screen:            
        if self.rect.left < screen.rect.left:
            if SOUNDS: SNDS[0].play()

            #Bounce from the left side:
            dir_radians = radians(self.direction)
            if cos(dir_radians) < 0:
                self.direction = (180-self.direction)%360
                self.rect.left = screen.rect.left + 1
                self.x = self.rect.x

        #And the right edge of the screen:
        if self.rect.right > screen.rect.right:
            if SOUNDS: SNDS[0].play()

            #Check the Ball's direction and bounce it:
            dir_radians = radians(self.direction)
            if cos(dir_radians) > 0:
                self.direction = (180-self.direction)%360
                self.rect.right = screen.rect.right - 1
                self.x = self.rect.x

        #And fall off the bottom of the screen:
        if self.rect.bottom >= screen.rect.bottom:
            
            #If not the last Ball, remove points and delete the Ball:
            if len(BALLS) > 1:
                player.multiplier = 1
                player.score = player.score *0.95
                print("\n[-5% score] - Lost a Ball!\n")
                print("Score:{:8}".format(round(player.score)))
                for l in [OBJECTS, BALLS]: l.remove(self)
            
            #If the last Ball falls:
            else:
                if player.lives > 1:
                    player.lives -= 1
                    player.score = player.score *0.9
                    print("\n[-10% score] - Lost the last Ball!\n")
                    print("Score:{:8}".format(round(player.score)))
                    print("Lives:{:8}\n".format(player.lives))
                    self.reset()
                else:
                    print("\n[GAME OVER] - No more lives!\n")
                    reset_game()
        
    def bounce(self,diff):

        if SOUNDS: SNDS[0].play()

        #Reverse the vertical direction, add some angle:
        self.direction = (360-self.direction)%360
        self.direction += diff*3

        #Don't get stuck inside the Paddle:
        dir_radians = radians(self.direction)
        if self.speed * sin(dir_radians) < 0:
            self.direction = (360-self.direction)%360
            self.rect.y -= 1

    def reset(self):

        #Reset the position of the Ball:
        self.rect.x, self.rect.y = self.x, self.y
        self.x = OBJECTS[0].rect.center[0] - (self.width/2) + 1
        self.y = OBJECTS[0].rect.center[1] - (self.height/2) - 11
        self.speed, self.direction = 0, 270

class New_Brick(pygame.sprite.Sprite):

    def __init__(self,x,y,health,color):
        pygame.sprite.Sprite.__init__(self)

        #Set up the width, height and health:
        self.width, self.height, self.health = 19, 9, health

        #The image and it's color:
        self.image = pygame.Surface([self.width, self.height])
        self.color = color; self.image.fill(self.color)

        #And the position of the rect:
        self.rect = pygame.Rect(screen.rect.left + x,
                                screen.rect.top + y,
                                self.width, self.height)
    def get_hit(self):

        #Remove health, if possible:
        if self.health > 1: self.health -= 1

        #Or just destroy the Brick, if no health left:
        else:
            #There is a pretty rare error, when two Balls hit a Brick
            #simultaneously and try to destroy it, we want to catch that.
            #It doesn't affect the game at all, though:
            try:
                for l in [OBJECTS, BRICKS]: l.remove(self)

                #Make the code below easier to read:
                player = OBJECTS[0]

                #Possibly, give a special bonus for destroying a brick:
                if (randint(1,10) == 1 and player.bonuses_enabled
                    and len(BRICKS) > 1):

                    #Select one of the random bonuses:
                    bonus_random = randint(1,4)
                    if bonus_random == 1: bonus = "extra_ball"
                    if bonus_random == 2: bonus = "large_board"
                    if bonus_random == 3: bonus = "small_board"
                    if bonus_random == 4: bonus = "time_distortion"
                    get_bonus = True

                    #An extra Ball bonus:
                    if bonus == "extra_ball":

                        #If there's already a Ball locked to
                        #the Paddle, don't give an extra one:
                        for ball in BALLS:
                            if ball.speed == 0:
                                get_bonus = False

                        if get_bonus:

                            if SOUNDS: SNDS[1].play()

                            #Create the Ball, add it to the lists,
                            #and inform the player of the bonus:
                            new_ball = New_Ball(False)
                            OBJECTS.append(new_ball)
                            BALLS.add(new_ball)
                            print("\n[BONUS] - An extra Ball!\n")

                    #A larger board bonus:
                    if bonus == "large_board" and not player.large_board:

                        if SOUNDS: SNDS[1].play()
                        player.large_board = True

                        #Resize the Paddle:
                        player.width = 60
                        player.image = pygame.Surface([player.width, player.height])
                        player.rect = pygame.Rect(player.x, player.y, player.width, player.height)
                        player.image.fill(WHITE)
                        
                        #Set the restore timer:
                        bonus_time = randint(5,10)
                        player.timer = bonus_time*60
                        print("\n[BONUS] - Larger Paddle for [{}] seconds!\n".format(bonus_time))

                    #A smaller board "bonus":
                    if bonus == "small_board" and not player.small_board:

                        if SOUNDS: SNDS[2].play()
                        player.small_board = True

                        #Resize the Paddle:
                        player.width = 15
                        player.image = pygame.Surface([player.width, player.height])
                        player.rect = pygame.Rect(player.x, player.y, player.width, player.height)
                        player.image.fill(WHITE)
                        
                        #Set the restore timer:
                        bonus_time = randint(5,10)
                        player.timer = bonus_time*60
                        print("\n[CURSE] - Smaller Paddle for [{}] seconds!\n".format(bonus_time))

                    #Time Distortion bonus:
                    if bonus == "time_distortion" and len(BALLS) > 1:

                        if SOUNDS: SNDS[1].play()
                        player.time_distortion = True

                        #Set all the moving(!) Balls' speed to 1:
                        for ball in BALLS:
                            if ball.speed > 0:
                                ball.speed = 1

                        #Set the restore timer:
                        bonus_time = randint(5,10)
                        player.timer = bonus_time*60
                        print("\n[BONUS] - Time Distortion for [{}] seconds!\n".format(bonus_time))
                    
            except ValueError:
                if DEBUG: print("\n[DEBUG] - Failed to remove an item from a list!\n")

        #Set the Brick color according to it's health:
        if self.health > 2: self.color = D_GRAY
        elif self.health == 2: self.color = L_GRAY
        elif self.health < 2: self.color = WHITE
        self.image.fill(self.color)

class New_Level_Select():

    def __init__(self,image,x,y,num,key):

        #The level number and key (in the keyboard) of the button:
        self.num, self.key = num, key

        #Set up the images (base and hovered over), and a timer:
        self.original_image = image
        self.image = self.original_image
        self.timer = 0

        #Some booleans:
        self.hovered = False
        self.pressed = False
        self.locked = True
        self.enabled = True

        #And then set up the rect:
        self.width = pygame.Surface.get_width(self.image)
        self.height = pygame.Surface.get_height(self.image)
        self.rect = pygame.Rect(screen.rect.left + x, screen.rect.top + y, self.width, self.height)
        
    def update(self):
        global LEVEL, game_mode

        #Change the image color, if hovered over or locked:
        if self.locked or not self.enabled:
            self.image = self.original_image.copy()
            replace_color(self.image, [WHITE], D_GRAY)
        elif self.hovered and not self.locked:
            self.image = self.original_image.copy()
            replace_color(self.image, [WHITE], L_GRAY)
        else: self.image = self.original_image

        #Count down the timer if above zero, enable self @ zero:
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.enabled = True

        #Check for mouse position or mouse or keyboard press:
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]
        key_press = pygame.key.get_pressed()

        #Load the level if self pressed and not self locked or disabled:
        if (self.pressed and self.hovered) or key_press[self.key]:
            if self.enabled:

                #Disable the button for a second:
                self.timer = 60
                self.enabled = False

                #Load the level:
                LEVEL = self.num
                game_mode = "ingame"
                load_level()

        #Check if the button is hovered over or pressed:
        if ((self.rect.left < mouse_pos[0] < self.rect.right) and
            (self.rect.top < mouse_pos[1] < self.rect.bottom)):
            
            if not self.locked: self.hovered = True
            if mouse_press and not self.locked: self.pressed = True
            else: self.pressed = False
            
        else: self.hovered, self.pressed = False, False

class New_Menu_Button():
    def __init__(self,x,y,image,key):

        #Set up the key (in the keyboard) and a timer:
        self.key = key
        self.timer = 0

        #The button's images (and those lil' bools):
        self.original_image = image
        self.image = self.original_image
        self.hovered = False
        self.locked = False

        #And, again, set up the rect:
        self.rect = pygame.Rect(screen.rect.left + x, screen.rect.top + y,
                                pygame.Surface.get_width(self.image),
                                pygame.Surface.get_height(self.image))
    def update(self):

        #Set the correct image color:
        if self.hovered and not self.locked:
            self.image = self.original_image.copy()
            replace_color(self.image, [WHITE], L_GRAY)
        elif self.locked:
            self.image = self.original_image.copy()
            replace_color(self.image, [WHITE, L_GRAY], D_GRAY)
        else: self.image = self.original_image

        #Count down the timer if above zero, unlock self at zero:
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.locked = False

        #Check for mouse pos and mouse/keyboard press:
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]
        key_press = pygame.key.get_pressed()

        #If mouse inside the button's rect:
        if ((self.rect.left < mouse_pos[0] < self.rect.right) and
            (self.rect.top < mouse_pos[1] < self.rect.bottom)):
            self.hovered = True
        else: self.hovered = False

        #Open the highscores text file:
        if (((mouse_press and self.hovered) or key_press[self.key])
            and not self.locked):

            print_scores()

            #Can't press the button again for half a second:
            self.timer = 30
            self.locked = True

def load_unlocked_levels():

    #Try to load the unlocked level progress from the "scores.txt":
    try:
        with open("games/breakout/scores.txt", 'r') as scores:
            row_num = 1
            for line in scores:
                if row_num == 12:
                    for btn in BUTTONS:
                        if btn.num <= int(line) or btn.num == 0:
                            btn.locked = False
                row_num += 1

    #If the file doesn't exist, default to 0:
    except FileNotFoundError:
        try:
            for btn in BUTTONS:
                if btn.num == 0:
                    btn.locked = False

        #Menu buttons passing through the loop:
        except AttributeError: pass
    except AttributeError: pass

def load_level():
    global LEVEL, game_mode

    if LEVEL > 9: reset_game(); return

    #Load the Bricks from the correct (.txt) level file:
    try:
        with open("games/breakout/levels/"+str(LEVEL)+".txt", 'r') as level:
            y_pos = 14
            description = False
            found_error = False

            #Go through each line in the file:
            for raw_line in level:
                x_pos = 16
                raw_line = raw_line.strip("\n")

                #If there are any level description lines, print them:
                if raw_line[0:4] == "DESC":
                    print(raw_line.split("=")[1])
                    description = True
                
                #And each letter of the line:
                for raw_letter in raw_line:
                    make_brick = True
                    unknown_brick = False

                    #Make the Brick according to the letter in the line:
                    if raw_letter == "1":
                        new_brick = New_Brick(x_pos, y_pos, 1, WHITE)
                    elif raw_letter == "2":
                        new_brick = New_Brick(x_pos, y_pos, 2, L_GRAY)
                    elif raw_letter == "3":
                        new_brick = New_Brick(x_pos, y_pos, 3, D_GRAY)
                    elif raw_letter == " " or raw_line[0:4] == "DESC":
                          make_brick = False
                          
                    #If the line is somehow incorrect:
                    else:
                        make_brick = False
                        unknown_brick = True
                        
                    #Just ignore it, but inform the Player:
                    if DEBUG and unknown_brick:
                        found_error = True
                        print('[DEBUG] - Unknown brick in level file "{}"{}'
                              .format('./games/breakout/levels/' + str(LEVEL) + '.txt',", ignoring"))
                    
                    if raw_line[0:4] == "DESC": make_brick = False

                    #Finally, append the Brick to the grand list:                
                    if make_brick:
                        OBJECTS.append(new_brick)
                        BRICKS.add(new_brick)
                    
                    x_pos += 20
                y_pos += 10
            
                if found_error:
                    print()
                    found_error = False
            
            if description: print()
            else: print("No Level description!\n")

            #Try to load a function assosiated to the level:
            try: exec("level_code_{}()".format(LEVEL))

            #No code?, fine:
            except NameError:
                if DEBUG: print("[DEBUG] - No special code for level {}\n".format(LEVEL))
                OBJECTS[0].timer = 1
                
            print("Press [Space] or [Mouse 2] to release the Ball!\n")
            print("Lives:{:8}\n".format(OBJECTS[0].lives))

    #If the level file is gone:
    except FileNotFoundError:
        print("[ERROR] - Can't find level file '{}.txt', returning to menu!".format(LEVEL))
        reset_game()

def level_code_9():

    #The grand finale, just one life, no bonuses,
    #and an infinite small paddle:

    #Set the vars:
    OBJECTS[0].timer = 0
    OBJECTS[0].lives = 1
    OBJECTS[0].bonuses_enabled = False
    OBJECTS[0].small_board = True

    #And resize the Paddle:
    OBJECTS[0].width = 15
    OBJECTS[0].image = pygame.Surface([OBJECTS[0].width, OBJECTS[0].height])
    OBJECTS[0].rect = pygame.Rect(OBJECTS[0].x, OBJECTS[0].y, OBJECTS[0].width, OBJECTS[0].height)
    OBJECTS[0].image.fill(WHITE)

    if DEBUG: print("[DEBUG] - Special code for level 9 loaded!\n")

def save_scores():

    #Check if the "scores.txt" exists, if not, make one:
    try: open("games/breakout/scores.txt", 'r').close()
    except FileNotFoundError: open("games/breakout/scores.txt", 'w').close()

    #Read the previous scores, make a list of the lines in the save file:
    with open("games/breakout/scores.txt", 'r') as scores:
        previous_scores = []
        for raw_line in scores:
            previous_scores.append(raw_line)

    #If there are no previous saved high scores, save the score,
    #and write "no data" to all the other levels:
    if not previous_scores:
        with open("games/breakout/scores.txt", 'w') as scores:

            #Max score (I do believe it's impossible, but just to be safe):
            if OBJECTS[0].score > 999999999999:
                OBJECTS[0].score = 999999999999
                
            for row_num in range(12):
                
                if row_num == LEVEL:
                    string = ("{}: {}\n".format(row_num, round(OBJECTS[0].score)))
                    print("\nNew Highscore for level {}! [{}]".format(LEVEL, round(OBJECTS[0].score)))

                #Also save the progress of unlocked levels:
                elif row_num == 10: string = "\n"
                elif row_num == 11: string = str(LEVEL+1)
                
                else: string = "{}: no data\n".format(row_num)
                
                scores.write(string)
                previous_scores.append(string)

    #If there are saved high scores, only write the new score
    #if it was more than the previous one, or if the level was new:
    else:
        with open("games/breakout/scores.txt", 'w') as scores:
            row_num = 0

            #Max score (I do believe it's impossible, but just to be safe):
            if OBJECTS[0].score > 999999999999:
                OBJECTS[0].score = 999999999999
            
            for line in previous_scores:
                
                if (row_num == LEVEL and
                    line.split(": ")[1].strip("\n") == "no data"):
                    scores.write("{}: {}\n".format(row_num, round(OBJECTS[0].score)))
                    print("\nNew Highscore for level {}! [{}]".format(LEVEL, round(OBJECTS[0].score)))
                    
                elif (row_num == LEVEL and float(line.split(": ")[1]) < OBJECTS[0].score):
                    scores.write("{}: {}\n".format(row_num, round(OBJECTS[0].score)))
                    print("\nNew Highscore for level {}! [{}]".format(LEVEL, round(OBJECTS[0].score)))

                #Save the progress of the unlocked levels:
                elif row_num == 10: scores.write("\n")
                elif row_num == 11 and int(line) <= LEVEL:
                    scores.write(str(LEVEL+1))
                    
                else: scores.write(line)
                row_num += 1

def print_scores():

    #Check if the "scores.txt" exists, if not, make one:
    try: open("games/breakout/scores.txt", 'r').close()
    except FileNotFoundError: open("games/breakout/scores.txt", 'w').close()

    #Read the previous scores line by line and print them:
    with open("games/breakout/scores.txt", 'r') as scores:
        firstline = scores.readline()
        if firstline == "":
            print("You have no highscores! Get on it!\n")
        else:
            row_num = 0
            print("LEVEL ~~~ SCORE")
            saves = [firstline]
            for score in scores: saves.append(score)
            for line in saves:
                line = line.strip("\n")
                if row_num < 10:
                    print("{}:{:>13}".format(line.split(":")[0], line.split(":")[1]))
                row_num += 1
            print()
    
def init(x,y):
    
    #Initialize the game, make the draggable box in the main window:
    return New_Game(x,y,load_image("game_breakout.png",game=True))

def load_sounds():
    global SNDS

    #Load all the sounds used:
    bounce = load_sound("general_bounce.ogg")
    powerup = load_sound("breakout_powerup.ogg")
    negative = load_sound("breakout_negative.ogg")

    #Pack 'em all up:
    SNDS = [bounce, powerup, negative]

def load_game(console):
    global screen, BALLS, OBJECTS, BRICKS, BUTTONS, LEVEL, BKG, game_mode

    #Set up various game objects and lists:
    
    game_mode = "menu"
    screen = New_Display(console)
    LEVEL = None
    
    if DEBUG: print()

    #The Player's Paddle:
    player = New_Paddle(100,159)
    OBJECTS = [player]

    #The initial Ball:
    ball = New_Ball()
    BALLS = pygame.sprite.Group()
    OBJECTS.append(ball)
    BALLS.add(ball)

    #Load the numbers (0-9) as a tileset:
    NUMS = load_tiles("font_numbers.png",4,5)

    #The button for the highscores:
    btn_imgs = load_tiles("breakout_buttons.png",46,5)
    btn_highscores = New_Menu_Button(19,137,btn_imgs[0][0],K_h)

    #And the background for the menu:
    BKG = load_image("breakout_menu.png")
    
    BRICKS = pygame.sprite.Group()

    #Set up the level selection buttons:
    BUTTONS = []
    positions = [[19,69], [39,69], [59,69], [79,69], [99,69],
                 [19,89], [39,89], [59,89], [79,89], [99,89]]
    keys = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]
    
    for btn in range(0,10):
        BUTTONS.append(New_Level_Select(NUMS[btn][0],positions[btn][0],
                                        positions[btn][1],btn,keys[btn]))
    BUTTONS.append(btn_highscores)

    #Load the sounds, if available:
    if SOUNDS: load_sounds()

    #Load the progress of unlocked levels:
    load_unlocked_levels()
    
    print("\nLoaded Breakout!\n")

def reset_game():
    global game_mode

    #Reset the player vars:
    OBJECTS[0].lives = 3
    OBJECTS[0].score = 0
    OBJECTS[0].multiplier = 1.0
    OBJECTS[0].bonuses_enabled = True

    #Remove all the Bricks:
    for brick in BRICKS:
        for l in [OBJECTS, BRICKS]: l.remove(brick)

    #And all but one Ball:
    for ball in BALLS:
        if len(BALLS) > 1:
            for l in [OBJECTS, BALLS]:
                l.remove(ball)
        else: ball.reset()

    #Unlock levels and return to the menu:
    load_unlocked_levels()
    game_mode = "menu"

def main(display):
    global game_mode

    #Draw the menu, if in it:
    if game_mode == "menu":
        display.blit(BKG, screen.rect)
        for btn in BUTTONS:
            btn.update()
            display.blit(btn.image, btn.rect)
        return

    #Go through each object, update and blit them:
    for obj in OBJECTS:
        if obj not in BRICKS: obj.update()
        display.blit(obj.image, obj.rect)

        #Check if any balls hit the Player:
        if obj in BALLS:
            
            balls_hit = pygame.sprite.spritecollide(OBJECTS[0],BALLS,False)
            
            if obj in balls_hit:
                OBJECTS[0].multiplier = 1
                obj.rect.bottom = OBJECTS[0].rect.top - 1
                obj.bounce(OBJECTS[0].rect.center[0] - obj.rect.center[0])
