#!usr/bin/env python3

# Version 1.1.2 25.2.2014
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

import pygame, os
from pygame.locals import *
from random import randint
from .classes import *

from time import sleep

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

class New_Cannon():

    def __init__(self,x,y,images,speed):

        #Setup the image & speed:
        self.images = images
        self.image = self.images[0][0]
        self.speed = speed

        #And the rect:
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.center = (x, y)

        #Shooting timer (can't spam that spacebar):
        self.shoot_timer = GAME[1] * 10
        self.can_shoot = False

        #Game reset timer (triggered after death):
        self.reset_timer = 0

        #Health & score
        self.health = 1
        self.alive = True
        self.score = 0
        self.alien_wave = 1

        #Increasing the game speed after each alien wave:
        self.increase_speed = 0

        #Powerups:
        self.double_shot = False
        self.quick_shot = False
        self.barrier = False
        self.powerup_timer = 0

    def update(self):

        #Temporary list names:
        ALIENS = OBJECTS[0]
        BRICKS = OBJECTS[1]
        BULLETS = OBJECTS[2]
        OTHERS = OBJECTS[4]

        #If a bullet hits the player:
        if len(BULLETS) > 0:
            for bullet in BULLETS:
                if self.rect.colliderect(bullet.rect):

                    if SOUNDS: SNDS[1].play()

                    #If no barrier:
                    if not self.barrier:
                        
                        #DESTROY THE CANNON and create an explosion:
                        self.alive = False
                        OTHERS.append(New_Effect(self.rect.center,"explosion_ship"))
                    else: BRICKS[-1].get_hit()

                    #Delete the bullet:
                    BULLETS.remove(bullet)
                    
        #Control the shooting timer:
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

            #At zero, allow the player to shoot:
            if self.shoot_timer <= 0:
                self.can_shoot = True

        #And the powerup timer:
        if self.powerup_timer > 0:
            self.powerup_timer -= 1

            #At zero, remove all powerups and reset the image:
            if self.powerup_timer <= 0:
                self.double_shot = False
                self.quick_shot = False
                self.image = self.images[0][0]

        #Get input:
        keys = pygame.key.get_pressed()

        #Control the player:
        if keys[K_LEFT]: self.rect.left -= self.speed
        if keys[K_RIGHT]: self.rect.right += self.speed

        #Shooty lasor:
        if keys[K_SPACE] and self.can_shoot:

            if SOUNDS: SNDS[0].play()

            self.can_shoot = False
            self.shoot_timer = GAME[1] * 10

            #Shoot bullets according to current bonuses:
            if self.powerup_timer <= 0:
                BULLETS.append(New_Bullet(self.rect.center[0] - 1, self.rect.top - 6, 5, -5))
                
            #Doubleshot:
            elif self.double_shot:
                BULLETS.append(New_Bullet(self.rect.center[0] - 7, self.rect.top - 6, 5, -5))
                BULLETS.append(New_Bullet(self.rect.center[0] + 5, self.rect.top - 6, 5, -5))
                
            #Quickshot:
            elif self.quick_shot:
                self.shoot_timer /= 2
                BULLETS.append(New_Bullet(self.rect.center[0] - 1, self.rect.top - 6, 4, -8))
                
            #Barrier:
            elif self.barrier:
                BULLETS.append(New_Bullet(self.rect.center[0] - 1, self.rect.top - 18, 5, -5))
                
        #Return to the menu:
        if keys[K_ESCAPE] and GAME[0] != "menu":
            reset_game()

        #Keep the player inside the screen:
        if self.rect.left < screen.rect.left:
            self.rect.left = screen.rect.left
        if self.rect.right > screen.rect.right:
            self.rect.right = screen.rect.right

        #Check for any remaining aliens:
        aliens_gone = False
        for alien_row in ALIENS:
            if len(alien_row) == 0:
                aliens_gone = True
        for alien_row in ALIENS:
            if len(alien_row) > 0:
                aliens_gone = False

        #If all gone, bring in another wave:
        if aliens_gone:
            self.alien_wave += 1
            if self.alien_wave == 2: wave_text = "More aliens approaching!"
            elif self.alien_wave == 3:
                wave_text = "Still more? How many of them are there!?"
            elif self.alien_wave == 4:
                wave_text = "MORE aliens!? This must be the last of them!"
            elif self.alien_wave == 50:
                wave_text = "How the hell did you make this far!?!?!?"
            elif self.alien_wave > 50:
                wave_text = "You have no life."
            else: wave_text = "Kill these bastards, there can't be much more!"
            print("\n[Wave {}] - {}\n".format(self.alien_wave, wave_text))
            
            if self.increase_speed > -3.5: self.increase_speed -= 0.25
            start_game(GAME[0], increase = self.increase_speed)

    def reset(self):

        #Reset some booleans:
        self.alive = True
        self.barrier = False
        self.double_shot = False
        self.quick_shot = False

        #Some vars:
        self.score = 0
        self.alien_wave = 1
        self.powerup_timer = 0

        #And these two:
        self.image = self.images[0][0]
        self.rect.center = (screen.rect.center[0], self.rect.center[1])

    def update_reset(self):

        #If the player has died, set the reset timer:
        if self.alive == False and self.reset_timer == 0:
            self.reset_timer = 201
                        
        #Game reset timer:
        if self.reset_timer > 0:
            self.reset_timer -= 1
            
            #Dialogue displayed at the end of the game:
            if self.reset_timer == 200:
                print("\n[GAME OVER] - You're dead!\n")

            #Save scores and quit to menu:
            if self.reset_timer <= 0:
                save_scores()
                reset_game()

class New_Alien():

    row_timer = 0

    def __init__(self,x,y,row,image,health):

        #Set up own health and row:
        self.health = health
        self.row = row

        #Image according to the health:
        self.original_image = image

        self.image = self.original_image.copy()
        if self.health > 2: replace_color(self.image, [WHITE], D_GRAY)
        elif self.health == 2: replace_color(self.image, [WHITE], L_GRAY)

        #A direction and a couple of timers:
        self.direction = "right"
        self.move_timer = GAME[1]
        self.shoot_timer = GAME[1] * (16 + randint(5,10))

        #And the rect:
        self.rect = pygame.Surface.get_rect(self.image)
        self.width = pygame.Surface.get_width(self.image)
        self.rect.x = screen.rect.left + 20 + x
        self.rect.y = screen.rect.top + 3 + y

        #For keeping the ship high enough:
        self.starting_height = self.rect.bottom

    def update(self,display):

        #For easier reading:
        ALIENS = OBJECTS[0]
        BRICKS = OBJECTS[1]
        BULLETS = OBJECTS[2]
        OTHERS = OBJECTS[4]

        #Control the shoot timer:
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

            #At zero, try to shoot (only if the player is still alive):
            if self.shoot_timer <= 0:
                if OTHERS[0].alive:
                    self.shoot(display)

        #If a bullet hits an alien:
        if len(BULLETS) > 0:
            for bullet in BULLETS:
                if self.rect.colliderect(bullet.rect):

                    if SOUNDS: SNDS[1].play()

                    #Remove health, if able, and add score:
                    if self.health > 1 and OTHERS[0].alive:

                        BULLETS.remove(bullet)
                        self.health -= 1

                        #Score to add, according to the difficulty:
                        if GAME[0] == "normal": score = 2
                        elif GAME[0] == "hard": score = 4
                        elif GAME[0] == "impossible": score = 6
                        else: score = 0

                        #Give +2 extra score if all safety walls are gone:
                        if len(BRICKS) > 0:
                            OTHERS[0].score += score
                            print("Score:{:8} [{:^+5}]".format(OTHERS[0].score, score))
                        else:
                            OTHERS[0].score += score + 2
                            print("Score:{:8} [{:^+5}]".format(OTHERS[0].score, score))

                        #Set the new color:
                        self.image = self.original_image.copy()
                        if self.health > 2:
                            replace_color(self.image, [WHITE], D_GRAY)
                        elif self.health == 2:
                            replace_color(self.image, [WHITE], L_GRAY)

                    #Or just..
                    elif OTHERS[0].alive:
                        
                        #KILL THE ALIEN:
                        try: ALIENS[self.row].remove(self)
                        except ValueError:
                            if DEBUG: print("\n[DEBUG] - Failed to remove an item from a list!\n")
                        BULLETS.remove(bullet)

                        #Create an explosion:
                        OTHERS.append(New_Effect(self.rect.center,"explosion_ship"))

                        #Points according to difficulty:
                        if GAME[0] == "normal": score = 8
                        elif GAME[0] == "hard": score = 10
                        elif GAME[0] == "impossible": score = 12
                        else: score = 0

                        #Award some points (+2 extra if safety walls are gone):
                        if OTHERS[0].alive and len(BRICKS) > 0:
                            OTHERS[0].score += score
                            print("Score:{:8} [{:^+5}]".format(OTHERS[0].score, score))
                        elif OTHERS[0].alive and len(BRICKS) <= 0:
                            OTHERS[0].score += score + 2
                            print("Score:{:8} [{:^+5}]".format(OTHERS[0].score, score))

                        #There's a 10% chance the player gets a powerup:
                        if randint(1,10) == 1:

                            #If he doesn't have one already:
                            if not OTHERS[0].powerup_timer > 0:

                                #Random powerup:
                                powerup = randint(1,3)
                                powerup_name = "default"

                                #Doubleshot:
                                if powerup == 1:
                                    OTHERS[0].image = OTHERS[0].images[0][1]
                                    OTHERS[0].double_shot = True
                                    OTHERS[0].powerup_timer = 600
                                    powerup_name = "Doubleshot"

                                #Quickshot:
                                elif powerup == 2:
                                    OTHERS[0].quick_shot = True
                                    OTHERS[0].powerup_timer = 450
                                    powerup_name = "Quickshot"

                                #Barrier:
                                elif powerup == 3 and not OTHERS[0].barrier:
                                    OTHERS[0].barrier = True
                                    powerup_name = "Shield"
                                    BRICKS.append(New_Wall(OTHERS[0].rect.center[0],
                                                           OTHERS[0].rect.top - 3,
                                                           GAME[5], 3, True))
                                    
                                print("\nYou gained a Power-Up! - [{}]\n".format(powerup_name))

                    #If the player has died, just
                    #play a sound & remove the bullet:
                    else:
                        if SOUNDS: SNDS[1].play()
                        BULLETS.remove(bullet)

    def update_row(self):

        #Control the move timer:
        if self.move_timer > 0:
            self.move_timer -= 1
            
            #When the timer hits zero, move:
            if self.move_timer <= 0:
                self.move()

        #And the row change timer:
        if New_Alien.row_timer > 0:
            New_Alien.row_timer -= 1

            #Change row when the timer hits zero (only if the
            #player is alive and we're not too low already):
            if New_Alien.row_timer <= 0:
                if OBJECTS[4][0].alive:
                    if not self.rect.bottom > self.starting_height + 90:
                        self.change_row()

    def move(self):

        #Easier to read list names:
        ALIENS = OBJECTS[0]
        BRICKS = OBJECTS[1]

        #Direction the alien ships will move:
        move_to = self.direction

        #Go through each ship on the same row:
        for alien in ALIENS[self.row]:

            #Change direction to right if the screen's left edge is hit:
            if alien.rect.left < screen.rect.left + 5: move_to = "right"

            #And to left when the right edge is hit:
            if alien.rect.right > screen.rect.right - 5: move_to = "left"

            self.direction = move_to

        #Move all the ships on the same row to the correct direction:
        for alien in ALIENS[self.row]:
            if move_to == "left":
                alien.rect.left -= 1
            elif move_to == "right":
                alien.rect.right += 1

        #Check for collision between the alien ships & safety walls:
        if len(BRICKS) > 0:
            for brick in BRICKS:
                if self.rect.colliderect(brick.rect):

                    if SOUNDS: SNDS[1].play()

                    #Totally destroy all the walls we hit:
                    BRICKS.remove(brick)

        #Set the timer to redo this function:
        self.move_timer = GAME[1]

    def change_row(self):

        ALIENS = OBJECTS[0]

        #Go through all alien ships and move them down 3px for each
        #row remaining. (Kill them fast, or they come down fast):
        for alien_row in ALIENS:
            for alien in alien_row:
                alien.rect.bottom += 3

        #Reset the timer:
        New_Alien.row_timer = GAME[1] * 240

    def shoot(self, display):

        #Temporary, easier to read list names:
        ALIENS = OBJECTS[0]
        BULLETS = OBJECTS[2]

        can_shoot = True

        #The bottom row can always shoot, but we
        #need special checks for the rows above:
        if self.row != 2:
                
            if len(ALIENS[self.row + 1]) == 6: can_shoot = False
            else:
                test_rect = pygame.Rect(self.rect.left - 4, self.rect.bottom + 1, self.rect.width + 8, 51)
                
                aliens_rect_list = []
                for alien_row in ALIENS:
                    for alien in alien_row:
                        if alien != self:
                            aliens_rect_list.append(alien.rect)

                for alien_rect in aliens_rect_list:
                    if test_rect.colliderect(alien_rect):
                        can_shoot = False

        #If the ship can shoot, there's a 25% chance it can't:
        if can_shoot:
            if randint(1,4) == 1: can_shoot = False 

        #If it gets this far, shoot a new Bullet:
        if can_shoot:
            if SOUNDS: SNDS[0].play()
            BULLETS.append(New_Bullet(self.rect.center[0] - 1, self.rect.bottom + 1, 5, 5))
            
        #Reset the timer:
        self.shoot_timer = GAME[1] * (20 + randint(5,10))

class New_Bullet(pygame.sprite.Sprite):
    
    def __init__(self,x,y,speed,direction):
        pygame.sprite.Sprite.__init__(self)

        #Set up the width, height and image:
        self.width, self.height = 3, 6
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(WHITE)

        #The rect:
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.x, self.rect.y = x, y

        #Increase bullet speed according to the difficulty:
        if GAME[0] in ["normal","hard"]: speed_up = 2
        elif GAME[0] == "impossible": speed_up = 3
        else: speed_up = 0
        
        #And a movement timer:
        self.speed = speed - speed_up
        self.move_timer = self.speed

        #Who shot Mr Bullet?
        self.direction = direction

    def update(self):

        #Temporary list names:
        BRICKS = OBJECTS[1]
        BULLETS = OBJECTS[2]
        OTHERS = OBJECTS[4]

        #Control the movement timer:
        if self.move_timer > 0:
            self.move_timer -= 1

            #Move self down when the timer hits zero:
            if self.move_timer <= 0:
                self.rect.y += self.direction
                self.move_timer = self.speed

        #If the bullet hits a brick:
        if len(BRICKS) > 0:
            for brick in BRICKS:
                if self.rect.colliderect(brick.rect):

                    #If the bullet was shot by an alien, damage it:
                    if self.direction > 0:
                        brick.get_hit()

                        #Create a small bullet explosion
                        OTHERS.append(New_Effect((self.rect.center[0],self.rect.top),"explosion_bullet"))

                    #Then just delete the bullet:
                    try: BULLETS.remove(self)
                    except ValueError:
                        print("\n[DEBUG] - Failed to remove an item from a list!\n")

        #Or another bullet:
        if len(BULLETS) > 1:
            for bullet in BULLETS:
                if self.rect.colliderect(bullet.rect) and bullet != self:

                    #Add a point:
                    OTHERS[0].score += 1
                    print("Score:{:8} [ +1  ]".format(OTHERS[0].score))

                    #Destroy both of the bullets, create a small explosion:
                    BULLETS.remove(bullet)
                    BULLETS.remove(self)

                    OTHERS.append(New_Effect(self.rect.center,"explosion_bullet"))

        #Remove self if going below or above the screen:
        if ((self.rect.bottom > screen.rect.bottom - 3) or
            (self.rect.top < screen.rect.top + 3)):
            BULLETS.remove(self)

class New_Wall(pygame.sprite.Sprite):
    
    def __init__(self,x,y,images,health,barrier=False):
        pygame.sprite.Sprite.__init__(self)

        #The starting images:
        self.images = images
        self.image = self.images[0][0]

        #Real image & color according to health:
        self.health = health
        if self.health > 2:
            self.image = self.images[0][0].copy()
            replace_color(self.image, [WHITE], D_GRAY)
        elif self.health == 2:
            self.image = self.images[0][1].copy()
            replace_color(self.image, [WHITE], L_GRAY)
        elif self.health < 2:
            self.image = self.images[0][2].copy()

        #And how come, the rect:
        self.rect = pygame.Surface.get_rect(self.image)
        self.rect.x = screen.rect.left + x
        self.rect.y = screen.rect.top + y
        self.barrier = barrier

    def update(self):

        #If it's a barrier wall, stay above the player:
        if self.barrier:
            OBJECTS[4][0].powerup_timer = 60
            self.rect.center = (OBJECTS[4][0].rect.center[0], OBJECTS[4][0].rect.top - 3)
            
    def get_hit(self):

        #Easier to read list names:
        BRICKS = OBJECTS[1]

        if SOUNDS: SNDS[1].play()

        #Remove health, if above one:
        if self.health > 1: self.health -= 1

        #Or just remove the brick:
        else:
            if OBJECTS[4][0].alive and not self.barrier:
                print("\nOh noes, we lost a wall!\n")
            BRICKS.remove(self)

            #If self is a barrier:
            if self.barrier:
                OBJECTS[4][0].barrier = False

        #Set the color according to the health:
        if self.health > 2:
            self.image = self.images[0][0].copy()
            replace_color(self.image, [WHITE], D_GRAY)
        elif self.health == 2:
            self.image = self.images[0][1].copy()
            replace_color(self.image, [WHITE], L_GRAY)
        elif self.health < 2:
            self.image = self.images[0][2].copy()

class New_Effect:

    def __init__(self,position,effect_type):

        #Animation speed default:
        self.speed = 4

        #Define the effect type and speed:
        if effect_type == "explosion_ship":
            self.images = OBJECTS[3][0]
        elif effect_type == "explosion_bullet":
            self.images = OBJECTS[3][1]

        #A lifetime:
        self.life_max = len(self.images[0])
        self.life_image = 0
        self.timer = self.speed
        self.alive = True

        #Set up the images:
        self.image = self.images[0][self.life_image]
        self.width = pygame.Surface.get_width(self.image)
        self.height = pygame.Surface.get_height(self.image)

        #And the rect:
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = position

    def update(self):

        #Control the animation timer:
        if self.timer > 0:
            self.timer -= 1

            #At zero, change image or die:
            if self.timer == 0:
                self.life_image += 1

                #Easier to read list names:
                OTHERS = OBJECTS[4]

                if self.life_image < self.life_max:
                    self.image = self.images[0][self.life_image]
                    self.timer = self.speed
                else:
                    self.alive = False
                    OTHERS.remove(self)

class New_Menu_Button():

    def __init__(self,image,x,y,name,key):

        #Name & key (in the keyboard) of the button:
        self.name, self.key = name, key
        
        #Set up the image and a timer:
        self.original_image = image
        self.image = self.original_image
        self.timer = 0

        #Some bools:
        self.hovered = False
        self.pressed = False
        self.enabled = True

        #And the rect:
        self.width = pygame.Surface.get_width(self.image)
        self.height = pygame.Surface.get_height(self.image)
        self.rect = pygame.Rect(screen.rect.left + x, screen.rect.top + y, self.width, self.height)
        
    def update(self):
        global GAME

        #Set the image color if hovered over:
        if self.hovered and self.enabled:
            self.image = self.original_image.copy()
            replace_color(self.image, [WHITE], L_GRAY)
        elif not self.enabled:
            self.image = self.original_image.copy()
            replace_color(self.image, [WHITE, L_GRAY], D_GRAY)
        else: self.image = self.original_image.copy()

        #Control the timer, enable self at zero:
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.enabled = True

        #Check for mouse pos and mouse/keyboard press:
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()[0]
        key_press = pygame.key.get_pressed()

        #If hovered over with the mouse:
        if ((self.rect.left < mouse_pos[0] < self.rect.right) and
            (self.rect.top < mouse_pos[1] < self.rect.bottom)):
            self.hovered = True
        else: self.hovered = False

        #Do something when pressed:
        if (((mouse_press and self.hovered) or key_press[self.key])
            and self.enabled):

            #Set game mode:
            if self.name in ["normal","hard","impossible"]:
                GAME[0] = self.name
                OBJECTS[4][0].increase_speed = 0
                start_game(self.name, increase = OBJECTS[4][0].increase_speed)

            #Print the highscores:
            elif self.name == "highscores":
                print_scores()

            self.timer = 30
            self.enabled = False

def save_scores():

    #Check if the "scores.txt" exists, if not, make one:
    try: open("games/invaders/scores.txt", 'r').close()
    except FileNotFoundError: open("games/invaders/scores.txt", 'w').close()
    
    #Read the previous scores, make a list of the lines in the save file:
    with open("games/invaders/scores.txt", 'r') as scores:
        previous_scores = []
        for raw_line in scores:
            previous_scores.append(raw_line)

    #If there are no previous saved high scores, save the score,
    #and write "no data" to all the other levels:
    if not previous_scores:
        with open("games/invaders/scores.txt", 'w') as scores:

            #Clear the list of previous scores,
            #make a list of the difficulty names:
            previous_scores.clear()
            diffs = ["normal", "hard", "impossible"]

            #Max score (unlikely for anyone to ever get):
            if OBJECTS[4][0].score > 9999999:
                OBJECTS[4][0].score = 9999999

            for row in range(3):

                #If we're on the row of the correct difficulty level:
                if GAME[0] == diffs[row]:

                    #It's automatically a new highscore:
                    print("New highscore for {} difficulty! [{}]\n"
                          .format(GAME[0].title(),OBJECTS[4][0].score))
                    string = ("{}:{}\n".format(GAME[0].title(),OBJECTS[4][0].score))

                #Else, it's automatically not set yet:
                else: string = ("{}:no data\n".format(diffs[row].title()))

                scores.write(string)
                previous_scores.append(string)

    #If there are saved high scores, only write the
    #new score if it was more than the previous one:
    else:
        with open("games/invaders/scores.txt", 'w') as scores:

            #Again, make a list of the difficulty levels, starting row is 0:
            diffs = ["normal","hard","impossible"]
            row_num = 0

            #Max score (unlikely for anyone to ever get):
            if OBJECTS[4][0].score > 9999999:
                OBJECTS[4][0].score = 9999999

            #Go through each previous score:
            for line in previous_scores:
                if row_num in [0, 1, 2]:

                    #Check the previous highscore, if any:
                    prev_score = previous_scores[row_num].split(":")[1]

                    #If we're on the row of the difficulty level:
                    if GAME[0] == diffs[row_num]:

                        #If the previous score is less than
                        #the current one, or nonexistant:
                        if ((prev_score == "no data\n") or (int(prev_score) < OBJECTS[4][0].score)):

                            #New highscore! Print it:
                            print("New highscore for {} difficulty! [{}]\n"
                                  .format(diffs[row_num].title(),OBJECTS[4][0].score))
                            string = ("{}:{}\n".format(diffs[row_num].title(),OBJECTS[4][0].score))
                            
                        #Or just re-write the old score:
                        else: string = previous_scores[row_num]
                    else: string = previous_scores[row_num]

                #Increase the row number and write the string:
                scores.write(string)
                row_num += 1
                
def print_scores():

    #Check if the "scores.txt" exists, if not, make one:
    try: open("games/invaders/scores.txt", 'r').close()
    except FileNotFoundError: open("games/invaders/scores.txt", 'w').close()

    #Read the previous scores line by line and print them:
    with open("games/invaders/scores.txt", 'r') as scores:
        firstline = scores.readline()
        if firstline == "": print("You have no highscores! Get on it!\n")
        else:

            #Make a list of all the scores:
            saves = [firstline]
            for line in scores: saves.append(line)

            #Print each one in a nice table:
            print("DIFFICULTY ~~~ SCORE")
            for line in saves:
                line = line.strip("\n")
                if line.split(":")[1] != "no data":
                    print("{:11}:{:8}".format(line.split(":")[0],int(line.split(":")[1])))
                else: print("{:11}: {}".format(line.split(":")[0],"no data"))
            print()

def init(x,y):
    
    #Initialize the game, make the draggable box in the main window:
    return New_Game(x,y,load_image("game_invaders.png",game=True))

def load_sounds():
    global SNDS
    
    #Load all the sounds used:
    shoot = load_sound("invaders_shoot.ogg")
    destroy = load_sound("invaders_destroy.ogg")

    #And pack 'em up:
    SNDS = [shoot, destroy]

def load_game(console):
    global screen, OBJECTS, GAME

    #Set up various game objects and lists:
    
    screen = New_Display(console)

    game_mode = "menu"
    game_speed = 4
    
    if DEBUG: print("")

    #Some lists:
    ALIENS, BRICKS, BULLETS = [],[],[]
    EFFECTS, OTHERS, BUTTONS = [],[],[]

    #Setup animated effects:
    EFFECTS = [load_tiles("invaders_explosion_ship.png",7,7),
               load_tiles("invaders_explosion_bullet.png",3,3)]

    #Load some images:
    aliens = load_tiles("invaders_aliens.png",9,7)
    cannons = load_tiles("invaders_cannons.png",9,5)
    wall = load_tiles("invaders_wall.png",8,2)
    barrier = load_tiles("invaders_barrier.png",11,3)
    menu_btns = load_tiles("invaders_buttons.png",46,5)
    game_menu = load_image("invaders_menu.png")

    #Some game settings:
    GAME = [game_mode, game_speed, game_menu, aliens, wall, barrier]

    player = New_Cannon(screen.rect.center[0],
                        screen.rect.bottom - 12, cannons, 2)
    
    OTHERS.append(player)
    OTHERS[0].alive = True

    #And the menu buttons:
    BUTTONS.append(New_Menu_Button(menu_btns[0][0],21,70,"normal",K_n))
    BUTTONS.append(New_Menu_Button(menu_btns[0][1],21,90,"hard",K_h))
    BUTTONS.append(New_Menu_Button(menu_btns[0][2],21,110,"impossible",K_i))
    BUTTONS.append(New_Menu_Button(menu_btns[0][3],21,140,"highscores",K_g))
    
    #Load the sounds, if available:
    if SOUNDS: load_sounds()

    #Pack it all up:
    OBJECTS = []
    append_list = [ALIENS, BRICKS, BULLETS, EFFECTS, OTHERS, BUTTONS]
    for l in append_list: OBJECTS.append(l)
    
    print("\nLoaded Invaders!\n")

def start_game(difficulty,increase=0):
    global OBJECTS, GAME

    #Reset some game vars:
    New_Alien.row_timer = GAME[1] * 240
    GAME[1] = 4

    #If the player has a barrier, save it:
    if OBJECTS[4][0].barrier:
        temp_barrier = OBJECTS[1][-1]

    #Remove all previous objects, just in case:
    OBJECTS[0].clear()
    OBJECTS[1].clear()
    OBJECTS[2].clear()

    #Easier reading:
    ALIENS = OBJECTS[0]
    BRICKS = OBJECTS[1]
    game_speed = GAME[1]

    if difficulty == "normal":

        #Set the game speed:
        game_speed = (4 + increase)
        
        #Set up three rows of 6 alien ships (with health between 1 and 3),
        #each row being a list inside the main aliens list:
        ALIENS = [[],[],[]]
        for column in range(6):
            for row in range(3):
                random_hp = randint(1,3)
                random_img = randint(0,2)
                ALIENS[row].append(New_Alien(column*31, row*27, row, GAME[3][0][random_img], random_hp))

        #Set up four safety walls with a health of 3:
        BRICKS = []
        for x_pos in range(4):
            BRICKS.append(New_Wall(30+x_pos*49, 130, GAME[4], 3))

    if difficulty == "hard":

        #Fasten up the game a bit:
        game_speed = (3 + increase)
        
        #Three rows of 6 alien ships (with health between 2 and 3):
        ALIENS = [[],[],[]]
        for column in range(6):
            for row in range(3):
                random_hp = randint(2,3)
                random_img = randint(0,2)
                ALIENS[row].append(New_Alien(column*31, row*27, row, GAME[3][0][random_img], random_hp))

        #Two safety walls with a health of 3:
        BRICKS = []
        BRICKS.append(New_Wall(65, 130, GAME[4], 3))
        BRICKS.append(New_Wall(142, 130, GAME[4], 3))

    if difficulty == "impossible":

        #Fasten up the game a bit more:
        game_speed = (2 + increase)

        #NO safety walls.
        
        #Three rows of 6 alien ships (with health of 3):
        ALIENS = [[],[],[]]
        for column in range(6):
            for row in range(3):
                random_img = randint(0,2)
                ALIENS[row].append(New_Alien(column*31, row*27, row, GAME[3][0][random_img], 3))
                
    #If the player had a barrier:
    if OBJECTS[4][0].barrier:
        BRICKS.append(temp_barrier)

    #Just to be safe:
    if game_speed < 0.5: game_speed = 0.5

    #For some reason we have to do this:
    OBJECTS[0] = ALIENS
    OBJECTS[1] = BRICKS
    GAME[1] = game_speed

def reset_game():
    global OBJECTS, GAME

    #Revive/reset the player:
    OBJECTS[4][0].reset()
    
    #Return to the menu:
    GAME[0] = "menu"

def main(display):

    #Better list names:
    ALIENS = OBJECTS[0]; BRICKS = OBJECTS[1]
    BULLETS = OBJECTS[2]; OTHERS = OBJECTS[4]
    BUTTONS = OBJECTS[5]

    #Draw the menu, when in it:
    if GAME[0] == "menu":
        display.blit(GAME[2], screen.rect)
        for btn in BUTTONS:
            btn.update()
            display.blit(btn.image, btn.rect)

    else: #Draw the game:
        
        #Update & blit all the effects and the player:
        if len(OTHERS) > 0:
            for obj in OTHERS:

                #That is, if they're alive:
                if obj.alive:
                    obj.update()
                    display.blit(obj.image, obj.rect)

            #If the player has died:
            if OTHERS[0].alive == False:
                OTHERS[0].update_reset()

        if len(ALIENS) > 0:
            
            #Update each alien ship row:
            for i in range(3):
                if len(ALIENS[i]) > 0:
                    ALIENS[i][0].update_row()

            #Update & blit all the alien ships:
            for alien_row in ALIENS:
                if len(alien_row) > 0:
                    for alien in alien_row:
                        alien.update(display)
                        display.blit(alien.image, alien.rect)

        #Then update & blit all the Bullets (if any):
        if len(BULLETS) > 0:
            for bullet in BULLETS:
                bullet.update()
                display.blit(bullet.image, bullet.rect)

        #Blit all the bricks/walls:
        if len(BRICKS) > 0:
            for brick in BRICKS:
                brick.update()
                display.blit(brick.image, brick.rect)
