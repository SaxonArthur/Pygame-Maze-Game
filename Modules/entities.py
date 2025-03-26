import pygame

pygame.mixer.init()

class Player:
    def __init__(self, game, pos, size):
        self.game = game
        self.pos = list(pos)
        self.size = size
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}

        self.action = ''
        self.flip = False
        self.ori = 'forward'
        self.collide = False
        self.set_action('idle/'+self.ori)

        self.footsteps = pygame.mixer.Sound('data/sfx/footsteps.wav')
        self.footsteps.set_volume(0.5)

        self.last_movement = [0,0]

    #Creates the player hitbox
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def testCollision(self, rect):
        return rect.colliderect(self.rect())

    #Handles which animation to play
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets['player/' + self.action].copy()

    def update(self, tilemap,  movement = (0,0)):

        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.collide = False

        frame_movement = (movement[0] , movement[1])

        self.pos[0] += frame_movement[0]

        #Collision detection logic
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around((self.pos[0] , self.pos[1])):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                    self.collide = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                    self.collide = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                    self.collide = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                    self.collide = True
                self.pos[1] = entity_rect.y

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement
        if (movement[0] != 0 or movement[1] != 0) and not pygame.mixer.get_busy():
            self.footsteps.play(loops = -1)
        elif (movement[0] == 0 and movement[1] == 0) and pygame.mixer.get_busy():
            self.footsteps.stop()

        #Logic for determining player movement type
        if movement[1] < 0:
            self.set_action('run/back')
            self.ori = 'back'
        elif movement[1] > 0:
            self.set_action('run/forward')
            self.ori = 'forward'
        elif movement[0] != 0:
            self.set_action('run/hori')
            self.ori = 'hori'
        else:
            self.set_action('idle/'+self.ori)
        if self.collide:
            self.set_action('idle/'+self.ori)

        self.animation.update()

    def render(self, surface, offset = (0,0)):
        surface.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))