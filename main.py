import pygame
from Parser import parse
import Tile
import time
from Actor import Actor
from Utils import *
from Spritesheet import Spritesheet
import random
import Text
  
class Main(object):
  def __init__(self):
    random.seed()
    self._SCREENW=256
    self._SCREENH=240
    self._MAPW=256
    self._MAPH=176
    self._OFFSET=self._SCREENH-self._MAPH
    self._FPS=60.0
    self._TICK=1.0/self._FPS
    
    self._zoom = 2
    self._quit = False
    pygame.init()
    size = width, height = self._SCREENW*self._zoom, self._SCREENH*self._zoom
    self._screen = pygame.display.set_mode(size)
    
    self._tiles, self._monsters = parse('first.map')
    self._lifetxt = Text.get('-LIFE-', (255,0,0))
    self._btxt = Text.get('X')[0]
    self._atxt = Text.get('Z')[0]
    
    iss = Spritesheet('icons.bmp')
    self._fullheart = iss.image_at((0,0,8,8), colorkey=(255,0,255))
    self._halfheart = iss.image_at((8,0,8,8), colorkey=(255,0,255))
    self._emptyheart = colorReplace(iss.image_at((0,0,8,8), colorkey=(255,0,255)), (((255,0,0), (255,227,171)),))
    
    self._uibox = {}
    self._uibox['ul'] = iss.image_at((0,8,8,8), colorkey=(255,0,255))
    self._uibox['v'] = iss.image_at((8,8,8,8), colorkey=(255,0,255))
    self._uibox['h'] = pygame.transform.rotate(self._uibox['v'], 90)
    self._uibox['ur'] = pygame.transform.flip(self._uibox['ul'], True, False)
    self._uibox['br'] = pygame.transform.flip(self._uibox['ur'], False, True)
    self._uibox['bl'] = pygame.transform.flip(self._uibox['ul'], False, True)
    
    self._uirupee, self._uikey, self._uibomb = iss.images_at(((0,16,8,8), (8,16,8,8), (16,16,8,8)), colorkey=(255,0,255))
    
    self._walls = [aabb for tile in self._tiles for aabb in tile.AABBs]
    #imgs = [pygame.image.load(tile.img) for tile in self._tiles]
    
    
    ss = Spritesheet('link.bmp')
    s = {}
    s[Direction.UP] = ss.images_at(((16,0,16,16),(16,16,16,16)), colorkey=(255,0,255))
    s[Direction.DOWN] = ss.images_at(((0,0,16,16),(0,16,16,16)), colorkey=(255,0,255))
    s[Direction.LEFT] = ss.images_at(((32,0,16,16),(32,16,16,16)), colorkey=(255,0,255))
    self._pc = Actor(15*8,11*8,2,s,12*16,8)
    
    self._actors = [self._pc] + self._monsters
    
    
  def setzoom(self, val):
    self._zoom = val
    size = width, height = self._SCREENW*self._zoom, self._SCREENH*self._zoom
    self._screen = pygame.display.set_mode(size)
    

  def main(self):
    nexttick = time.time()+self._TICK
    while not self._quit:
      if time.time() >= nexttick:
        nexttick += self._TICK
        self._update()
        self._render()
    
  def _update(self):
    [actor.update() for actor in self._actors]
    self._input()
    self._physics()
    
  def _render(self):
    self._screen.fill((0,0,0))
    
    for tile in self._tiles:
      self._screen.blit(pygame.transform.scale(tile.img, (Tile.SIZE*self._zoom, Tile.SIZE*self._zoom)), ((tile.x)*self._zoom, (tile.y+self._OFFSET)*self._zoom))
    for actor in self._actors:
      sprite = actor.sprite
      self._screen.blit(pygame.transform.scale(sprite, (sprite.get_width()*self._zoom, sprite.get_height()*self._zoom)), ((actor.x+actor.xoffset)*self._zoom, (actor.y+self._OFFSET+actor.yoffset)*self._zoom))
      
    self._renderui()
      
    pygame.display.flip()

    
  def _renderui(self):
    for i in range(len(self._lifetxt)):
      self._screen.blit(self._getzoom(self._lifetxt[i]), ((23+i)*8*self._zoom, 16*self._zoom))
    self._screen.blit(self._getzoom(self._atxt), ((19)*8*self._zoom, 16*self._zoom))
    self._screen.blit(self._getzoom(self._btxt), ((16)*8*self._zoom, 16*self._zoom))
    
    ul = self._getzoom(self._uibox['ul'])
    ur = self._getzoom(self._uibox['ur'])
    br = self._getzoom(self._uibox['br'])
    bl = self._getzoom(self._uibox['bl'])
    v = self._getzoom(self._uibox['v'])
    h = self._getzoom(self._uibox['h'])
    for i in range(2):
      self._screen.blit(ul, ((3*i+15)*8*self._zoom, 2*8*self._zoom))
      self._screen.blit(ur, ((3*i+17)*8*self._zoom, 2*8*self._zoom))
      self._screen.blit(br, ((3*i+17)*8*self._zoom, 5*8*self._zoom))
      self._screen.blit(bl, ((3*i+15)*8*self._zoom, 5*8*self._zoom))
      self._screen.blit(h, ((3*i+16)*8*self._zoom, 5*8*self._zoom))
      for j in range(4):
        self._screen.blit(v, ((3*i+2*(j%2)+15)*8*self._zoom, (j/2+3)*8*self._zoom))
    self._screen.blit(self._getzoom(self._uirupee), (11*8*self._zoom, 2*8*self._zoom))
    self._screen.blit(self._getzoom(self._uikey), (11*8*self._zoom, 4*8*self._zoom))
    self._screen.blit(self._getzoom(self._uibomb), (11*8*self._zoom, 5*8*self._zoom))
    for i in range(4):
      if i == 1:
        continue
      x0 = Text.get('X0')
      for j in range(len(x0)):
        self._screen.blit(self._getzoom(x0[j]), ((j+12)*8*self._zoom,(i+2)*8*self._zoom))
    maprect = pygame.Surface((8*8, 8*4))
    maprect.fill((100,100,100))
    self._screen.blit(self._getzoom(maprect), (2*8*self._zoom, 2*8*self._zoom))    
        
    for i in range(self._pc.maxhp/16):
      heart = self._fullheart
      if self._pc.hp > i*16 and self._pc.hp <= i*16+8:
        heart = self._halfheart
      elif self._pc.hp <= i*16:
        heart = self._emptyheart
      self._screen.blit(self._getzoom(heart), ((22+i%8)*8*self._zoom, (6-i/8)*8*self._zoom))
      
  def _getzoom(self, surf):
    return pygame.transform.scale(surf, (surf.get_width()*self._zoom, surf.get_height()*self._zoom))
  
  def _input(self):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self._quit = True
        return
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_1]:
      self.setzoom(1)
    if keys[pygame.K_2]:
      self.setzoom(2)
    if keys[pygame.K_3]:
      self.setzoom(3)
    if keys[pygame.K_4]:
      self.setzoom(4)
    
    if self._pc.isControllable:
      dx = 0
      dy = 0
      
      if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
        self._pc.incframe()

      if keys[pygame.K_DOWN] or keys[pygame.K_UP]:
        if keys[pygame.K_DOWN]:
          if self._pc.x % 8 == 0:
            dy += self._pc.speed
            self._pc.direction = Direction.DOWN
          elif self._pc.direction == Direction.LEFT:
            dx -= self._pc.speed
          elif self._pc.direction == Direction.RIGHT:
            dx += self._pc.speed
        if keys[pygame.K_UP]:
          if self._pc.x % 8 == 0:
            dy -= self._pc.speed
            self._pc.direction = Direction.UP
          elif self._pc.direction == Direction.LEFT:
            dx -= self._pc.speed
          elif self._pc.direction == Direction.RIGHT:
            dx += self._pc.speed
      else:
        if keys[pygame.K_LEFT]:
          if self._pc.y % 8 == 0:
            dx -= self._pc.speed
            self._pc.direction = Direction.LEFT
          elif self._pc.direction == Direction.UP:
            dy -= self._pc.speed
          elif self._pc.direction == Direction.DOWN:
            dy += self._pc.speed
        if keys[pygame.K_RIGHT]:
          if self._pc.y % 8 == 0:
            dx += self._pc.speed
            self._pc.direction = Direction.RIGHT
          elif self._pc.direction == Direction.UP:
            dy -= self._pc.speed
          elif self._pc.direction == Direction.DOWN:
            dy += self._pc.speed
      self._pc.dx += dx
      self._pc.dy += dy
    for monster in self._monsters:
      monster.incframe()
      if monster.ai == 'random':
        if random.randint(1,20) == 20:
          monster.dx = 0
          monster.dy = 0
          if (monster.dx != 0 and monster.x % 8 == 0) or (monster.dy != 0 and monster.y % 8 == 0) or (monster.dx == 0 and monster.dy == 0):
            d = (None, Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)[random.randint(0,4)]
            if d is not None:
              monster.direction = d
              if d == Direction.UP:
                monster.dy -= monster.speed
              if d == Direction.DOWN:
                monster.dy += monster.speed
              if d == Direction.LEFT:
                monster.dx -= monster.speed
              if d == Direction.RIGHT:
                monster.dx += monster.speed
        
          
  def _physics(self):
    for actor in self._actors:
      if actor.x <= 0:
        actor.x = 0
      if actor.y <= 0:
        actor.y = 0
      if actor.x+16 >= self._MAPW:
        actor.x = self._MAPW-16
      if actor.y+16 >= self._MAPH:
        actor.y = self._MAPH-16
        
      actor.x += actor.dx
      for wall in self._walls:
        if actor.aabb.colliderect(wall):
          if actor.dx < 0:
            actor.x = wall.x+wall.w
          else:
            actor.x = wall.x-actor.aabb.w
      actor.y += actor.dy
      for wall in self._walls:
        if actor.aabb.colliderect(wall):
          if actor.dy < 0:
            actor.y = wall.y+wall.h
          else:
            actor.y = wall.y-actor.aabb.h
    
    if self._pc.isControllable:    
      self._pc.dx = 0
      self._pc.dy = 0
            
    for monster in self._monsters:
      if self._pc.aabb.colliderect(monster.aabb) and not self._pc.isInvincible:
        self._pc.hurt(monster.attack)
        self._pc.becomeInvincible(30)
        self._pc.loseControl(8)
        speed = self._pc.speed*2
        if self._pc.direction == Direction.UP:
          self._pc.dy = speed
        if self._pc.direction == Direction.DOWN:
          self._pc.dy = -speed
        if self._pc.direction == Direction.LEFT:
          self._pc.dx = speed
        if self._pc.direction == Direction.RIGHT:
          self._pc.dx = -speed
          
          
if __name__ == '__main__':
  Main().main()