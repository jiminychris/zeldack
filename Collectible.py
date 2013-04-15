import pygame

class Collectible(object):
  def __init__(self, x, y, aabb, sprites, condition, action, triumph):
    self._x = x
    self._y = y
    self._aabb = aabb
    self._sprites = sprites
    self._condition = condition
    self._action = action
    self._triumph = triumph

    self._frame = 0
    self._anim = 0

  def update(self):
    self._frame += 1
    if self._frame == 8:
      self._frame = 0
      self._anim = (self._anim + 1) % len(self._sprites)

  @property
  def x(self):
    return self._x
  @property
  def y(self):
    return self._y
  @property
  def aabb(self):
    return pygame.Rect(self._aabb.x+self._x, self._aabb.y+self._y,self._aabb.w,self._aabb.h)
  @property
  def sprite(self):
    return self._sprites[self._anim]
  @property
  def condition(self):
    return self._condition
  @property
  def action(self):
    return self._action
  @property
  def triumph(self):
    return self._triumph