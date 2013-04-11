import pygame

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)
  
def colorReplace(surf, swaps):
  s = surf.copy()
  pa = pygame.PixelArray(s)
  for swap in swaps:
    src = swap[0]
    dest = swap[1]
    [row.replace(src, dest) for row in pa]
    
  return s
    

Direction = enum("UP", "DOWN", "LEFT", "RIGHT")