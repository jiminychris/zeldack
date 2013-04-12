import pygame
from Parser import parse
import Tile
import time
from Actor import Actor
from Inventory import Inventory
from Utils import *
from Spritesheet import Spritesheet
import random
import Text
  
class Play(object):
  def __init__(self):
    random.seed()
    self._SCREENW=256
    self._SCREENH=240
    self._MAPW=256
    self._MAPH=176
    self._OFFSET=self._SCREENH-self._MAPH
    
    self._UBOUND = pygame.Rect(0, 0, self._MAPW, 8)
    self._RBOUND = pygame.Rect(self._MAPW, 0, 8, self._MAPH)
    self._BBOUND = pygame.Rect(0, self._MAPH, self._MAPW, 8)
    self._LBOUND = pygame.Rect(-8, 0, 8, self._MAPH)
    
    self._TEXTSPEED=4
    
    self._sword = None
    
    self._zoom = 2
    pygame.init()
    size = width, height = self._SCREENW*self._zoom, self._SCREENH*self._zoom
    self._screen = pygame.display.set_mode(size)
    
    linkpalette = (((0,0,0),(0,0,0)),((128,128,128),(200,76,12)),((192,192,192),(128,208,16)),((255,255,255),(252,152,56)))
    wss = Spritesheet('weapons.bmp')
    self._swordsprite = colorReplace(wss.image_at((0,0,8,16), colorkey=(0,0,0)), linkpalette)
    ssprite = self._swordsprite
    lssprite = pygame.transform.rotate(ssprite,90)
    self._swordsprites = {x:y for x,y in zip(DIRECTIONS, (ssprite, pygame.transform.flip(ssprite,False,True), lssprite, pygame.transform.flip(lssprite,True,False)))}
    self._lifetxt = Text.get('-LIFE-', (255,0,0))
    self._btxt = Text.get('Z')[0]
    self._atxt = Text.get('X')[0]
    
    iss = Spritesheet('icons.bmp')
    heart = iss.image_at((0,0,8,8), colorkey=(0,0,0))
    self._fullheart = colorReplace(heart, (((128,128,128),(255,0,0)),))
    self._halfheart = colorReplace(iss.image_at((8,0,8,8), colorkey=(0,0,0)), (((128,128,128),(255,0,0)),((255,255,255),(255,227,171))))
    self._emptyheart = colorReplace(heart, (((128,128,128),(255,227,171)),))
    
    self._uibox = {}
    self._uibox['ul'] = colorReplace(iss.image_at((0,8,8,8), colorkey=(0,0,0)), (((128,128,128),(0,89,250)),))
    self._uibox['v'] = colorReplace(iss.image_at((8,8,8,8), colorkey=(0,0,0)), (((128,128,128),(0,89,250)),))
    self._uibox['h'] = pygame.transform.rotate(self._uibox['v'], 90)
    self._uibox['ur'] = pygame.transform.flip(self._uibox['ul'], True, False)
    self._uibox['br'] = pygame.transform.flip(self._uibox['ur'], False, True)
    self._uibox['bl'] = pygame.transform.flip(self._uibox['ul'], False, True)
    
    self._uirupee, self._uikey, self._uibomb = iss.images_at(((0,16,8,8), (8,16,8,8), (16,16,8,8)), colorkey=(0,0,0))
    self._uirupee = colorReplace(self._uirupee, (((128,128,128),(255,161,68)),((255,255,255),(255,227,171))))
    self._uikey = colorReplace(self._uikey, (((128,128,128),(255,161,68)),))
    self._uibomb = colorReplace(self._uibomb, (((192,192,192),(0,89,250)),))
    
    
    ss = Spritesheet('link.bmp')
    s = {}
    s[Direction.UP] = [colorReplace(sp, (((0,0,0),(0,0,0)),((128,128,128),(200,76,12)),((192,192,192),(128,208,16)),((255,255,255),(252,152,56)))) for sp in ss.images_at(((16,0,16,16),(16,16,16,16)), colorkey=(0,0,0))]
    s[Direction.DOWN] = [colorReplace(sp, (((0,0,0),(0,0,0)),((128,128,128),(200,76,12)),((192,192,192),(128,208,16)),((255,255,255),(252,152,56)))) for sp in ss.images_at(((0,0,16,16),(0,16,16,16)), colorkey=(0,0,0))]
    s[Direction.LEFT] = [colorReplace(sp, (((0,0,0),(0,0,0)),((128,128,128),(200,76,12)),((192,192,192),(128,208,16)),((255,255,255),(252,152,56)))) for sp in ss.images_at(((32,0,16,16),(32,16,16,16)), colorkey=(0,0,0))]
    atks = {}
    atks[Direction.UP] = colorReplace(ss.image_at((16,32,16,16), colorkey=(0,0,0)), linkpalette)
    atks[Direction.DOWN] = colorReplace(ss.image_at((0,32,16,16), colorkey=(0,0,0)), linkpalette)
    atks[Direction.LEFT] = colorReplace(ss.image_at((32,32,16,16), colorkey=(0,0,0)), linkpalette)
    self._pc = Actor(15*8,11*8,2,3*16,8,pygame.Rect(0, 0, Tile.SIZE, Tile.HALF),True,s,atksprites=atks)
    self._inventory = Inventory()
    self._pcweapons = []
    
    self._start()
    
  def _start(self):
    self._pc.x = 15*8
    self._pc.y = 11*8
    self._loadmap('first.map')
    
    
  @property
  def inventory(self):
    return self._inventory
    
  @property
  def _actors(self):
    return self._monsters + self._pcweapons + [self._pc]
  @property
  def _bounders(self):
    return [actor for actor in self._actors if actor.wallcollisions]
    
  def _loadmap(self, m):
    self._tiles, self._monsters, self._decos, self._portals, self._textlist = parse(m, self)
    self._texttimer = 0
    self._texttimermax = len(self._textlist)*self._TEXTSPEED
    self._pc.stop()
    self._pc.loseControl(self._texttimermax)
    
  def setzoom(self, val):
    self._zoom = val
    size = width, height = self._SCREENW*self._zoom, self._SCREENH*self._zoom
    self._screen = pygame.display.set_mode(size)
  
  def _attacks(self):
    if self._pc.isAttacking and self._sword is None:
      atk = self._inventory.sword*8
      sprite = {Direction.UP: [self._swordsprite]}
      w=3
      l=11
      if self._pc.direction == Direction.UP:
        x,y,r = self._pc.x+3, self._pc.y-9-l, pygame.Rect(2, 0, w, l)
      elif self._pc.direction == Direction.RIGHT:
        x,y,r = self._pc.x+12, self._pc.y-3, pygame.Rect(6, 3, l, w)
      elif self._pc.direction == Direction.DOWN:
        x,y,r = self._pc.x+5, self._pc.y+4, pygame.Rect(2, 6, w, l)
      else:# self._pc.direction == Direction.LEFT:
        x,y,r = self._pc.x-12, self._pc.y-3, pygame.Rect(0, 3, l, w)
      self._sword = Actor(x,y,0,0,atk,r,False,sprite)
      self._sword.direction = self._pc.direction
      self._sword.setoffsets(0,0)
      self._pcweapons.append(self._sword)
    elif not self._pc.isAttacking and self._sword is not None:
      self._pcweapons.remove(self._sword)
      self._sword = None  
  
  def _deaths(self):
    if self._pc.hp == 0:
      self._pc.heal(self._pc.maxhp)
      self._start()
    self._monsters = [monster for monster in self._monsters if monster.hp > 0]
  
  def _update(self):
    self._attacks()
    self._deaths()
    [updater.update() for updater in self._actors+self._decos]
    if self._texttimer < self._texttimermax:
      self._texttimer += 1
    self._input()
    self._physics()
    
  def _render(self):
    self._screen.fill((0,0,0))
    
    for tile in self._tiles:
      self._screen.blit(pygame.transform.scale(tile.img, (Tile.SIZE*self._zoom, Tile.SIZE*self._zoom)), ((tile.x)*self._zoom, (tile.y+self._OFFSET)*self._zoom))
    for deco in self._decos:
      self._screen.blit(self._getzoom(deco.sprite), (deco.x*self._zoom, (deco.y+self._OFFSET)*self._zoom))   
    for tile in self._textlist[:self._texttimer/self._TEXTSPEED]: 
      self._screen.blit(self._getzoom(tile.img), (tile.x*self._zoom, (tile.y+self._OFFSET)*self._zoom))
    for actor in self._actors:
      sprite = actor.sprite
      self._screen.blit(pygame.transform.scale(sprite, (sprite.get_width()*self._zoom, sprite.get_height()*self._zoom)), ((actor.x+actor.xoffset)*self._zoom, (actor.y+self._OFFSET+actor.yoffset)*self._zoom))
      
    self._renderui()
    
    #self._renderaabbdebug()
    
    pygame.display.flip()

  def _renderaabbdebug(self):
    for aabb in [actor.aabb for actor in self._actors]:
      r = self._getzoom(pygame.Surface((aabb.w, aabb.h)))
      r.fill((255,0,255))
      self._screen.blit(r, (aabb.x*self._zoom, (aabb.y+self._OFFSET)*self._zoom))
  
  
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
    if self._inventory.sword > 0:
      self._screen.blit(self._getzoom(self._swordsprite), (19*8*self._zoom, 3*8*self._zoom))
    self._screen.blit(self._getzoom(self._uirupee), (11*8*self._zoom, 2*8*self._zoom))
    self._screen.blit(self._getzoom(self._uikey), (11*8*self._zoom, 4*8*self._zoom))
    self._screen.blit(self._getzoom(self._uibomb), (11*8*self._zoom, 5*8*self._zoom))
    rupees = Text.get(('X' if self._inventory.rupees < 100 else '')+str(self._inventory.rupees))
    for i in range(len(rupees)):
      self._screen.blit(self._getzoom(rupees[i]), ((i+12)*8*self._zoom,(2)*8*self._zoom))
    keys = Text.get('X'+str(self._inventory.keys))
    for i in range(len(keys)):
      self._screen.blit(self._getzoom(keys[i]), ((i+12)*8*self._zoom,(4)*8*self._zoom))
    bombs = Text.get('X'+str(self._inventory.bombs))
    for i in range(len(bombs)):
      self._screen.blit(self._getzoom(bombs[i]), ((i+12)*8*self._zoom,(5)*8*self._zoom))
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
      self._pc.dx = dx
      self._pc.dy = dy
      
      if keys[pygame.K_x]:
        if self._pc.canAttack and self._inventory.sword > 0:
          self._pc.doAttack(16)
          self._pc.loseControl(16)
          self._pc.stop()
      else:
        self._pc.releaseAttack()
      
    for monster in self._monsters:
      monster.incframe()
      if monster.isControllable:
        if monster.ai == 'random':
          if random.randint(1,20) == 20:
            dx = 0
            dy = 0
            if (monster.dx != 0 and monster.x % 8 == 0) or (monster.dy != 0 and monster.y % 8 == 0) or (monster.dx == 0 and monster.dy == 0):
              d = (None, Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)[random.randint(0,4)]
              if d is not None:
                monster.direction = d
                if d == Direction.UP:
                  dy -= monster.speed
                if d == Direction.DOWN:
                  dy += monster.speed
                if d == Direction.LEFT:
                  dx -= monster.speed
                if d == Direction.RIGHT:
                  dx += monster.speed
            monster.dx = dx
            monster.dy = dy
          
  def _physics(self):
    for actor in self._bounders:
      p = None
      if actor.aabb.colliderect(self._UBOUND):
        p = self._portals[Direction.UP]
        actor.y = self._UBOUND.y+self._UBOUND.h
      if actor.aabb.colliderect(self._RBOUND):
        p = self._portals[Direction.RIGHT]
        actor.x = self._RBOUND.x-actor.aabb.w
      if actor.aabb.colliderect(self._BBOUND):
        p = self._portals[Direction.DOWN]
        actor.y = self._BBOUND.y-actor.aabb.h
      if actor.aabb.colliderect(self._LBOUND):
        p = self._portals[Direction.LEFT]
        actor.x = self._LBOUND.x+self._LBOUND.w
      if p is not None and actor is self._pc:
        return self._port(p)
        
      actor.x += actor.dx
      for tile in self._tiles:
        for wall in tile.AABBs:
          if actor.aabb.colliderect(wall):
            if actor.dx < 0:
              actor.x = wall.x+wall.w
            else:
              actor.x = wall.x-actor.aabb.w
      actor.y += actor.dy
      for tile in self._tiles:
        for wall in tile.AABBs:
          if actor.aabb.colliderect(wall):
            if actor is self._pc and tile.isPortal:
              return self._port(tile.portal)
            else:
              if actor.dy < 0:
                actor.y = wall.y+wall.h
              else:
                actor.y = wall.y-actor.aabb.h
            
    for monster in self._monsters:
      for weapon in self._pcweapons:
        if monster.aabb.colliderect(weapon.aabb) and not monster.isInvincible:
          monster.hurt(weapon.attack)
          monster.becomeInvincible(30)
          monster.loseControl(8)
          monster.stop()
          speed = self._pc.speed*2
          if self._pc.direction == Direction.UP:
            monster.dy = -speed
          if self._pc.direction == Direction.DOWN:
            monster.dy = speed
          if self._pc.direction == Direction.LEFT:
            monster.dx = -speed
          if self._pc.direction == Direction.RIGHT:
            monster.dx = speed
          
      if self._pc.aabb.colliderect(monster.aabb) and not self._pc.isInvincible:
        self._pc.hurt(monster.attack)
        self._pc.becomeInvincible(30)
        self._pc.loseControl(8)
        self._pc.stop()
        if not self._pc.isAttacking:
          speed = self._pc.speed*2
          if monster.direction == Direction.UP:
            self._pc.dy = -speed
          if monster.direction == Direction.DOWN:
            self._pc.dy = speed
          if monster.direction == Direction.LEFT:
            self._pc.dx = -speed
          if monster.direction == Direction.RIGHT:
            self._pc.dx = speed
      
  def _port(self, portal):
    self._inventory.changesword(1)
    self._loadmap(portal.destfile)
    self._pc.x = portal.destx
    self._pc.y = portal.desty  
    
class Game(object):
  def __init__(self):
    self._FPS=60.0
    self._TICK=1.0/self._FPS
    self._play = Play()
    self._quit = False
    
  def main(self):
    nexttick = time.time()+self._TICK
    while not self._quit:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self._quit = True
          return
      if time.time() >= nexttick:
        nexttick += self._TICK
        self._play._update()
        self._play._render()
  
    
if __name__ == '__main__':
  Game().main()