import pygame
from Parser import parse
import Tile
import time
from Actor import Actor
from Utils import *
from Spritesheet import Spritesheet
import random
  
SCREENW=256
SCREENH=240
MAPW=256
MAPH=176
OFFSET=SCREENH-MAPH
ZOOM=2
FPS=60.0
TICK=1.0/FPS

def main():
  quit = False
  random.seed()
  pygame.init()
  size = width, height = SCREENW*ZOOM, SCREENH*ZOOM
  screen = pygame.display.set_mode(size)
  
  tiles, monsters = parse('first.map')
  walls = [aabb for tile in tiles for aabb in tile.AABBs]
  #imgs = [pygame.image.load(tile.img) for tile in tiles]
  
  
  #ss = Spritesheet('link.bmp')
  ss = Spritesheet('octorok.bmp')
  s = {}
  s[Direction.UP] = ss.images_at(((0,0,16,16),(0,16,16,16)), colorkey=(255,0,255))
  #s[Direction.UP] = ss.images_at(((16,0,16,16),(16,16,16,16)), colorkey=(255,0,255))
  #s[Direction.DOWN] = ss.images_at(((0,0,16,16),(0,16,16,16)), colorkey=(255,0,255))
  #s[Direction.LEFT] = ss.images_at(((32,0,16,16),(32,16,16,16)), colorkey=(255,0,255))
  pc = Actor(100,100,2,s)
  
  actors = [pc] + monsters
  
  nexttick = time.time()+TICK
  while not quit:
    if time.time() >= nexttick:
      nexttick += TICK
      quit = update(pc, walls, monsters)
      render(screen, actors, tiles, ZOOM)
  
def update(pc, walls, monsters):
  if input(pc, monsters):
    return True
  physics(pc, walls, monsters)
  
def render(screen, actors, tiles, zoom):
  screen.fill((0,0,0))
  """border = pygame.Surface((8*16*2*zoom,8*15*2*zoom))
  border.fill((255,255,0))
  tile = pygame.Surface((6*zoom,6*zoom))
  tile.fill((50,50,50))
  screen.blit(border,(0,0))"""
  for tile in tiles:
    screen.blit(pygame.transform.scale(tile.img, (Tile.SIZE*zoom, Tile.SIZE*zoom)), ((tile.x)*zoom, (tile.y+OFFSET)*zoom))
  for actor in actors:
    sprite = actor.sprite
    screen.blit(pygame.transform.scale(sprite, (sprite.get_width()*zoom, sprite.get_height()*zoom)), ((actor.x+actor.xoffset)*zoom, (actor.y+OFFSET+actor.yoffset)*zoom))
  pygame.display.flip()

def input(pc, monsters):
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      return True
  keys = pygame.key.get_pressed()
  pc.dx = 0
  pc.dy = 0
  
  if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
    pc.incframe()

  if keys[pygame.K_DOWN] or keys[pygame.K_UP]:
    if keys[pygame.K_DOWN]:
      if pc.x % 8 == 0:
        pc.dy += pc.speed
        pc.direction = Direction.DOWN
      elif pc.direction == Direction.LEFT:
        pc.dx -= pc.speed
      elif pc.direction == Direction.RIGHT:
        pc.dx += pc.speed
    if keys[pygame.K_UP]:
      if pc.x % 8 == 0:
        pc.dy -= pc.speed
        pc.direction = Direction.UP
      elif pc.direction == Direction.LEFT:
        pc.dx -= pc.speed
      elif pc.direction == Direction.RIGHT:
        pc.dx += pc.speed
  else:
    if keys[pygame.K_LEFT]:
      if pc.y % 8 == 0:
        pc.dx -= pc.speed
        pc.direction = Direction.LEFT
      elif pc.direction == Direction.UP:
        pc.dy -= pc.speed
      elif pc.direction == Direction.DOWN:
        pc.dy += pc.speed
    if keys[pygame.K_RIGHT]:
      if pc.y % 8 == 0:
        pc.dx += pc.speed
        pc.direction = Direction.RIGHT
      elif pc.direction == Direction.UP:
        pc.dy -= pc.speed
      elif pc.direction == Direction.DOWN:
        pc.dy += pc.speed
        
  for monster in monsters:
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
      
        
def physics(pc, walls, monsters):
  for actor in [pc] + monsters:
    if actor.x <= 0:
      actor.x = 0
    if actor.y <= 0:
      actor.y = 0
    if actor.x+16 >= MAPW:
      actor.x = MAPW-16
    if actor.y+16 >= MAPH:
      actor.y = MAPH-16
      
    actor.x += actor.dx
    for wall in walls:
      if actor.aabb.colliderect(wall):
        if actor.dx < 0:
          actor.x = wall.x+wall.w
        else:
          actor.x = wall.x-actor.aabb.w
    actor.y += actor.dy
    for wall in walls:
      if actor.aabb.colliderect(wall):
        if actor.dy < 0:
          actor.y = wall.y+wall.h
        else:
          actor.y = wall.y-actor.aabb.h
        
        
if __name__ == '__main__':
  main()