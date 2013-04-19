import pygame

SIZE = 16
HALF = SIZE/2

class Tile(object):
  def __init__(self, x, y, img, aabbs=None, portal=None, mask=False):
    self._x = x
    self._y = y
    self._img = img
    self._condition = 'True'
    self._portal = portal
    self._mask = mask
    if aabbs is None:
      aabbs = ()
    self._aabbs = aabbs

  def addcond(self, cond):
    self._condition = cond
    
  @property
  def condition(self):
    return self._condition
  @property
  def x(self):
    return self._x
    
  @property
  def y(self):
    return self._y
    
  @property
  def isPortal(self):
    return self._portal is not None
    
  @property
  def portal(self):
    return self._portal
    
  @property
  def img(self):
    return self._img
  
  @property
  def aabbs(self):
    return [pygame.Rect(aabb.x+self._x, aabb.y+self._y, aabb.w, aabb.h) for aabb in self._aabbs]
    
  @property
  def mask(self):
    return self._mask
