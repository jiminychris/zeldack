import pygame

SIZE = 16
HALF = SIZE/2

class Tile(object):
  def __init__(self, x, y, img, AABBs, portal=None):
    self._x = x * SIZE
    self._y = y * SIZE
    self._img = img
    self._portal = portal
    if AABBs is None:
      AABBs = ()
    self._AABBs = map(lambda x: pygame.Rect(x.x*HALF+self._x, x.y*HALF+self._y, x.w*HALF, x.h*HALF), AABBs)
    
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
  def AABBs(self):
    return map(lambda x: pygame.Rect(x), self._AABBs)