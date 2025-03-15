import pygame
import tkinter as tk
from tkinter import filedialog
import json
import random

#Used to search tiles directly around player
NEIGHBOUR_OFFSET = [(-1,0), (-1,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (0,-1), (0,0)]

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.last_color = [255, 100, 0]

    def create_circle_overlay(self,  screen_width, screen_height,radius = 15):
        self.circle_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        red = max(200, min(self.last_color[0] + random.randint(-2,2), 230))
        green = max(0, min(self.last_color[1] + random.randint(-5,5), 100))
        blue = max(0, min(self.last_color[2] + random.randint(-2,2), 10))
        self.last_color = (red, green, blue)

        self.circle_surf.fill((0,0,0, 255))
        pygame.draw.circle(self.circle_surf, (self.last_color[0], self.last_color[1], self.last_color[2],30), (screen_width//2,screen_height//2), radius)
    
    def tiles_around(self, pos):
        tiles=[]
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOUR_OFFSET:
            check_loc = str(tile_loc[0]+offset[0])+';'+str(tile_loc[1]+offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap' : self.tilemap, 'tile_size' : self.tile_size, 'offgrid':self.offgrid_tiles}, f)
        f.close()

    def load(self):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        file_path = filedialog.askopenfilename(initialdir="/Users/saxon/Projects/Pygame/data/maps", filetypes=[("Json files", "*.json")])
        if file_path:
            f = open(file_path, 'r')
            data = json.load(f)
            self.tilemap = data['tilemap']
            self.tile_size = data['tile_size']
            self.offgrid_tiles = data['offgrid']
            f.close()

    def load_from_path(self, path):
        f = open(path, 'r')
        data = json.load(f)
        self.tilemap = data['tilemap']
        self.tile_size = data['tile_size']
        self.offgrid_tiles = data['offgrid']
        f.close()

    def clear(self):
        self.tilemap = {}
        self.offgrid_tiles = []

    #Checks if the tiles around are walls for collision
    def physics_rects_around(self, pos):
        self.rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] == 'walls':
                self.rects.append(pygame.Rect(tile['pos'][0]*self.tile_size, tile['pos'][1]*self.tile_size, self.tile_size, self.tile_size))
        return self.rects
    
    #Grid style rendering, tiles contain a calculated position
    def render(self, surf, offset=(0,0), editor = True):
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile['type'] == 'resize':
                        surf.blit(pygame.transform.scale(self.game.assets[tile['type']][tile['variant']], (16,16)), (x * self.tile_size - offset[0], y * self.tile_size - offset[1]))
                    else:
                        surf.blit(self.game.assets[tile['type']][tile['variant']], (x * self.tile_size - offset[0], y * self.tile_size - offset[1]))

        for tile in self.offgrid_tiles:
            if tile['type'] == 'resize':
                surf.blit(pygame.transform.scale(self.game.assets[tile['type']][tile['variant']], (16,16)), (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            else:
                surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        if not editor:
            surf.blit(self.circle_surf, (0,0))
