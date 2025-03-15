import pygame
from pygame.locals import *
import sys
import pyautogui
import random

#Importing objects
from Modules.tilemap import Tilemap
from Modules.utils import load_image, load_images, Animation
from Modules.entities import Player

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        self.my_font = pygame.freetype.SysFont('Comic Sans MS', 10)

        #Handles pop up screens and buttons
        self.game_state = 'Start'
        self.start_clicked = False
        self.lose_restart_clicked = False
        self.win_restart_clicked = False

        #Retrieves resolution of display
        self.x, self.y = pyautogui.size()[0], pyautogui.size()[1] *0.93

        #Coordinates for different maps
        self.map_data = {
            0 : {
                'spawn': (58, 150),
                'end' : pygame.Rect(474, 130, 20 ,60)
            },
            1 : {
                'spawn' : (345, 170),
                'end' : pygame.Rect(-96, 167, 60, 20)
            },
            2 : {
                'spawn' : (185, 250),
                'end' : pygame.Rect(32, -32, 40, 60)
            }
        }
        self.randmap = random.randint(0,2)

        pygame.display.set_caption('Lost Treasure')
        self.screen = pygame.display.set_mode((self.x, self.y))
        self.display = pygame.Surface((self.x/8, self.y/8))
        self.clock = pygame.time.Clock()
        self.timer = 7200

        self.movement = [False, False, False,  False]

        #Loading images, animations and sound effects using util.py
        self.assets = {
            'floor': load_images('tiles/floor'),
            'walls': load_images('tiles/walls'),
            'treasure' : load_images('tiles/treasure'),
            'resize' : load_images('tiles/resize'),
            'player/idle/back' : Animation(load_images('player/idle/back')),
            'player/run/back' : Animation(load_images('player/run/back')),
            'player/idle/forward' : Animation(load_images('player/idle/forward')),
            'player/run/forward' : Animation(load_images('player/run/forward')),
            'player/idle/hori' : Animation(load_images('player/idle/hori')),
            'player/run/hori' : Animation(load_images('player/run/hori')),
            'screens/startScreen/Title' : load_image('screens/startScreen/Title.png'),
            'screens/startScreen/StartFalse' : load_image('screens/startScreen/StartFalse.png'),
            'screens/startScreen/StartTrue' : load_image('screens/startScreen/StartTrue.png'),
            'screens/loseScreen' : Animation(load_images('screens/loseScreen')),
            'screens/RestartFalse' : load_image('screens/RestartFalse.png'),
            'screens/RestartTrue' : load_image('screens/RestartTrue.png'),
            'screens/winScreen' : Animation(load_images('screens/winScreen')),
            'sfx/win' : pygame.mixer.Sound('data/sfx/Win.wav'),
            'sfx/lose' : pygame.mixer.Sound('data/sfx/Lose.wav'),
            'sfx/ambience' : pygame.mixer.music.load('data/sfx/ambience.mp3')
        }

        pygame.mixer.music.set_volume(0.5)

        #This creates the player object
        self.player = Player(self, self.map_data[self.randmap]['spawn'], (14, 16))

        #Map object loaded from json file
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load_from_path('data/maps/'+str(self.randmap)+'.json')

        self.scroll = [0, 0]

        self.start_rect = pygame.Rect(self.display.get_width() / 4.2, self.display.get_height() / 1.5, self.display.get_width() / 1.8, self.display.get_height() / 5)
        self.restart_rect = pygame.Rect(self.display.get_width()/7, self.display.get_height()/1.32, self.display.get_width()/1.35, self.display.get_height() / 5.3)

        self.lose_screen_anim = self.assets['screens/loseScreen'].copy()
        self.win_screen_anim = self.assets['screens/winScreen'].copy()


    def run(self):
        pygame.mixer.music.play()
        while True:
            self.display.fill((0,0,0))
            mouse_x, mouse_y = pygame.mouse.get_pos()

            #This is a method to keep the player in the center of the screen by creating an offset
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0])
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1])
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            #Creates the circle around the torch and renders the map
            self.tilemap.create_circle_overlay(self.display.get_width() , self.display.get_height(), self.x // 60)
            self.tilemap.render(self.display, offset = render_scroll, editor=False)

            #Updates player movement
            self.player.update(self.tilemap, (self.movement[3] - self.movement[2], self.movement[1]- self.movement[0]))
            self.player.render(self.display, offset=render_scroll)

            #These if statements handle the current screen display, controlled by the variable game_state
            if self.game_state == "Start":
                if self.start_rect.collidepoint((mouse_x/8,mouse_y/8)):
                    self.start_clicked = True
                else:
                    self.start_clicked = False
                self.display.blit(pygame.transform.scale(self.assets['screens/startScreen/Title'], (self.display.get_width() / 2 ,self.display.get_height() / 3)), (self.display.get_width() / 3.8, self.display.get_height() / 12))
                self.display.blit(pygame.transform.scale(self.assets['screens/startScreen/Start'+str(self.start_clicked)], (self.display.get_width() / 1.8 , self.display.get_height() / 5)), (self.display.get_width() / 4.1, self.display.get_height()/1.5))
            
            if self.game_state == 'Lose':
                if self.restart_rect.collidepoint((mouse_x/8, mouse_y/8)):
                    self.lose_restart_clicked = True
                else:
                    self.lose_restart_clicked = False

                self.display.blit(pygame.transform.scale(self.lose_screen_anim.img(), (self.display.get_width(), self.display.get_height() * 0.7)), (0, 0))
                self.display.blit(pygame.transform.scale(self.assets['screens/Restart'+str(self.lose_restart_clicked)], (self.display.get_width(), self.display.get_height() * 0.3)), (0, self.display.get_height() * 0.7))
                self.lose_screen_anim.update()

            if self.game_state == 'Win':
                if self.restart_rect.collidepoint((mouse_x/8, mouse_y/8)):
                    self.win_restart_clicked = True
                else:
                    self.win_restart_clicked = False

                self.display.blit(pygame.transform.scale(self.win_screen_anim.img(), (self.display.get_width(), self.display.get_height() * 0.7)), (0, 0))
                self.display.blit(pygame.transform.scale(self.assets['screens/Restart'+str(self.win_restart_clicked)], (self.display.get_width(), self.display.get_height() * 0.3)), (0, self.display.get_height() * 0.7))
                self.win_screen_anim.update()

            if self.game_state == 'Playing':

                if self.timer <= 0:
                    self.game_state = 'Lose'
                    pygame.mixer.music.pause()
                    pygame.mixer.pause()
                    self.assets['sfx/lose'].play()
                    continue

                #Tests if the player has made it to the end
                if self.player.testCollision(self.map_data[self.randmap]['end']):
                    self.game_state = 'Win'
                    pygame.mixer.music.pause()
                    pygame.mixer.pause()
                    self.assets['sfx/win'].play()
                    continue
                self.timer -= 1
                self.my_font.render_to(self.display, (0, 0), 'Time Left: '+str(self.timer // 60), (250, 250, 250))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.game_state == "Start":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1 and self.start_clicked:
                            self.game_state = "Playing"
                            self.start_clicked = False
                elif self.game_state == "Lose" or self.game_state == "Win":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1 and (self.lose_restart_clicked or self.win_restart_clicked):
                            self.__init__() #Handy way of restarting the game

                #Handles all the movement key logic
                if self.game_state == 'Playing':

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            self.movement[0] = True
                        if event.key == pygame.K_s:
                            self.movement[1] = True
                        if event.key == pygame.K_a:
                            self.movement[2] = True
                        if event.key == pygame.K_d:
                            self.movement[3] = True
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_w:
                            self.movement[0] = False
                        if event.key == pygame.K_s:
                            self.movement[1] = False
                        if event.key == pygame.K_a:
                            self.movement[2] = False
                        if event.key == pygame.K_d:
                            self.movement[3] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()
