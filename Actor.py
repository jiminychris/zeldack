import Tile
import pygame
from Utils import *

class Actor(object):
  def __init__(self, x, y, speed, sprites, ai=None):
    self._x = x
    self._y = y
    self._dx = 0
    self._dy = 0
    self._speed = speed
    self._xoffset = 0
    self._yoffset = -Tile.HALF
    self._frame = 0
    self._anim = 0
    self._ai = ai
    self._sprites = sprites
    if sprites is None or Direction.UP not in sprites.keys():
      raise ValueError('Expected at least UP sprite in dict')
    if Direction.DOWN not in sprites.keys():
      self._sprites[Direction.DOWN] = map(lambda s: pygame.transform.flip(s, False, True), sprites[Direction.UP])
    if Direction.LEFT not in sprites.keys():
      self._sprites[Direction.LEFT] = map(lambda s: pygame.transform.rotate(s, 90), sprites[Direction.UP])
    if Direction.RIGHT not in sprites.keys():
      self._sprites[Direction.RIGHT] = map(lambda s: pygame.transform.flip(s, True, False), self._sprites[Direction.LEFT])
    self.direction = Direction.DOWN
    
  @property
  def x(self):
    return self._x
  @x.setter
  def x(self, value):
    self._x = value
    
  @property
  def y(self):
    return self._y
  @y.setter
  def y(self, value):
    self._y = value
    
  @property
  def xoffset(self):
    return self._xoffset
    
    
  @property
  def yoffset(self):
    return self._yoffset
    
  @property
  def speed(self):
    return self._speed
    
  @property
  def dx(self):
    return self._dx
  @dx.setter
  def dx(self, value):
    self._dx = value
    
  @property
  def dy(self):
    return self._dy
  @dy.setter
  def dy(self, value):
    self._dy = value
    
  @property
  def ai(self):
    return self._ai
    
  @property
  def aabb(self):
    return pygame.Rect(self._x, self._y, Tile.SIZE, Tile.HALF)
    
  @property
  def sprite(self):
    return self._sprites[self.direction][self._anim]
    
  def incframe(self, value=1):
    self._frame += value
    while self._frame > 8: 
      self._frame -= 8
      self._anim = (self._anim + 1) % 2
      
    