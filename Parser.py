import xml.etree.ElementTree as et
from Tile import Tile
from pygame.rect import Rect
from Actor import Actor
from Spritesheet import Spritesheet
import random
from Utils import *

def parse(fname):
  random.seed()
  tree = _safeopen(fname)
  
  tilelist = []
  monsterlist = []
  
  root = tree.getroot()
  monsterfiles = map(lambda r: r.text, root.find('monsterfiles').findall('ref'))
  monroots = map(lambda f: _safeopen(f).getroot(), monsterfiles)
  rows = root.find('tiles').findall('row')
  monsters = root.find('monsters').findall('monster')
  
  for j in range(len(rows)):
    tiles = rows[j].findall('tile')
    for i in range(len(tiles)):
      t = tiles[i].get('type', 'blank')
      tilelist.append(Tile(i, j, _img(t), _aabbs(t)))
      
  for monster in monsters:
    id = monster.get('id', 'octorok')
    m = None
    for monroot in monroots:
      m = monroot.find(id)
      if m is not None:
        break
    if m is None:
      raise ValueError('could not find monster with id \''+id+'\' in '+str(monroots))
      
    hp = m.find('hp')
    if hp is None:
      hp = 8
    else:
      hp = int(hp.text)
      
    atk = m.find('attack')
    if atk is None:
      atk = 8
    else:
      atk = int(atk.text)
      
    pattern = None
    speed = 0
    aimov = m.find('ai')
    if aimov is not None:
      aimov = aimov.find('movement')
    if aimov is not None:
      speed = aimov.find('speed')
      pattern = aimov.find('pattern')
      
    if speed is not 0:
      options = speed.findall('option')
      if options is not None:
        speed = int(options[random.randint(0,len(options)-1)].text)
    if pattern is not None:
      pattern = pattern.text
    monsterlist.append(Actor(int(monster.get('x', '0')), int(monster.get('y', '0')), speed, _sprites(m), hp, atk, pattern))
      
  return tilelist, monsterlist
  
def _sprites(node):
  s = node.find('sprites')
  sheet = s.get('sheet', None)
  
  if sheet is None:
    raise ValueError('Expected a spritesheet')
    
  ss = Spritesheet(sheet)
    
  udlr = ((Direction.UP, s.find('up')), 
         (Direction.DOWN, s.find('down')), 
         (Direction.LEFT, s.find('left')), 
         (Direction.RIGHT, s.find('right')))
         
  repl = s.find('colors')
  if repl is not None:
    repl = [[_parsecolor(c) for c in r.findall('color')] for r in repl.findall('replace')]
  if udlr[0][1] is None:
    raise ValueError('Cannot do sprite without an UP direction')
    
  sd = {}
  for d in udlr:
    dir = d[0]
    xml = d[1]
    if xml is not None:
      slices = [[int(a) for a in (s.get('x','0'), s.get('y', '0'), s.get('w', '16'), s.get('h', '16'))] for s in xml.findall('sprite')]
      ck = xml.find('colorkey')
      if ck is not None:
        ck = _parsecolor(ck.find('color'))
      imgs = ss.images_at(slices, colorkey=ck)
      sd[dir] = imgs if repl is None else [colorReplace(img, repl) for img in imgs]
      
  return sd
  
def _parsecolor(node):
  return (int(node.get('r', '0')), int(node.get('g', '0')), int(node.get('b', '0')))
  
def _safeopen(fname):
  if not isinstance(fname, str):
    raise TypeError("Expected filename of type str")
  tree = None
  try:
    tree = et.parse(fname)
  except IOError as e:
    raise e
    
  return tree
      
def _aabbs(t):
  if t == 'wall' or t == 'wall-top':
    return (Rect(0,0,2,2),)
  elif t == 'top-left-corner':
    return (Rect(0,0,2,1), Rect(0,1,1,1))
  elif t == 'top-right-corner':
    return (Rect(0,0,2,1), Rect(1,1,1,1))
  elif t == 'bottom-left-corner':
    return (Rect(0,0,1,1), Rect(0,1,2,1))
  elif t == 'bottom-right-corner':
    return (Rect(1,0,1,1), Rect(0,1,2,1))
  else:
    return ()
    
def _img(t):
  return t.replace('-', '') + '.bmp'
  