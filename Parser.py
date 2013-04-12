import xml.etree.ElementTree as et
import Tile
from Portal import Portal
import Text
from pygame.rect import Rect
from Actor import Actor
from Spritesheet import Spritesheet
from Decoration import Decoration
import random
from Utils import *

_DEFAULTCOLORS = ((0,0,0),(128,128,128),(192,192,192),(255,255,255))
_DIRECTIONS = (Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT)

def parse(fname, main):
  random.seed()
  tree = _safeopen(fname)
  
  tilelist = []
  monsterlist = []
  decolist = []
  portals = {}
  textlist = []
  
  
  root = tree.getroot()
  textnode = root.find('text')
  if textnode is not None:
    textlist = [tile for line in textnode.findall('line') for tile in _parseline(line)]
  tiledefs = {}
  aabbdefs = {}
  portdefs = {}
  decodefs = {}
  portn = root.find('portals')
  ports = (_parseport(portn.find('up')), _parseport(portn.find('right')), _parseport(portn.find('down')), _parseport(portn.find('left')))
  portals = dict(zip(_DIRECTIONS, ports))
  
  dn = root.find('decorations')
  if dn is not None:
    dss = Spritesheet(dn.get('file', None))
    [decodefs.update(((d.get('type', 'blank'), ([colorReplace(s, zip(_DEFAULTCOLORS, _parsecolors(d.find('palette')))) for s in dss.images_at(_parsesprites(d), _tryparsecolorkey(d))], d.get('animtype', 'fliph'))),)) for d in dn.findall('def')]
    [decolist.append(Decoration(int(d.get('x', '0')), int(d.get('y', '0')), decodefs[d.get('type', 'blank')][0], decodefs[d.get('type', 'blank')][1])) for d in dn.findall('decoration')]
  tn = root.find('tiles')
  pn = tn.find('palette')
  palette = _parsecolors(pn)
  repl = zip(_DEFAULTCOLORS, palette)
  tss = Spritesheet(tn.get('file', None))
  [tiledefs.update(((d.get('type', 'blank'), colorReplace(tss.image_at(_parsesprite(d.find('sprite'))), repl)),)) for d in tn.findall('def')]
  [aabbdefs.update(((d.get('type', 'blank'), _parserects(d)),)) for d in tn.findall('def')]
  [portdefs.update(((d.get('type', 'blank'), _parseport(d)),)) for d in tn.findall('def')]
  monsterfiles = root.find('monsterfiles')
  rows = tn.findall('row')
  monsters = root.find('monsters')
  if monsters is not None:
    monsterfile = monsters.get('file', 'monsters.mon')
    monroot = _safeopen(monsterfile).getroot()
    monsters = monsters.findall('monster')
  else:
    monsters = []
  
  for j in range(len(rows)):
    tiles = rows[j].findall('tile')
    for i in range(len(tiles)):
      t = tiles[i].get('type', 'blank')
      tilelist.append(Tile.Tile(i, j, tiledefs[t], aabbdefs[t], portdefs[t]))
      
  for monster in monsters:
    id = monster.get('id', 'octorok')
    m = None
    m = monroot.find(id)
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
    monsterlist.append(Actor(int(monster.get('x', '0')), int(monster.get('y', '0')), speed, hp, atk, pygame.Rect(0, 0, Tile.SIZE, Tile.HALF), _sprites(m), None, pattern))
      
  return tilelist, monsterlist, decolist, portals, textlist
  
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
         
  repl = zip(_DEFAULTCOLORS, _parsecolors(s.find('palette')))
  if udlr[0][1] is None:
    raise ValueError('Cannot do sprite without an UP direction')
    
  sd = {}
  for d in udlr:
    dir = d[0]
    xml = d[1]
    if xml is not None:
      slices = _parsesprites(xml)
      ck = xml.find('colorkey')
      if ck is not None:
        ck = _parsecolor(ck.find('color'))
      imgs = ss.images_at(slices, colorkey=ck)
      sd[dir] = imgs if repl is None else [colorReplace(img, repl) for img in imgs]
      
  return sd
  
def _parsecolor(node):
  return (int(node.get('r', '0')), int(node.get('g', '0')), int(node.get('b', '0')))
def _parsecolors(node):
  return [_parsecolor(c) for c in node.findall('color')]
def _parsesprite(node):
  return [int(a) for a in (node.get('x','0'), node.get('y', '0'), node.get('w', '16'), node.get('h', '16'))]
def _parsesprites(node):
  return [_parsesprite(s) for s in node.findall('sprite')]
def _parserect(node):
  return pygame.Rect([int(a) for a in (node.get('x','0'), node.get('y', '0'), node.get('w', '16'), node.get('h', '16'))])
def _parserects(node):
  return [_parserect(r) for r in node.findall('rect')]
def _parseport(node):
  if node is None:
    return node
  port = node.find('portal')
  if port is not None:
    port = Portal(port.get('file', 'swordcave.map'), int(port.get('x', '0')), int(port.get('y', '0')))
  return port
def _tryparsecolorkey(node):
  if node is None:
    return None
  ck = node.find('colorkey')
  if ck is None:
    return None
  return _parsecolor(ck.find('color'))
def _parseline(node):
  x = int(node.get('x', '0'))
  y = int(node.get('y', '0'))
  txt = Text.get(node.get('value', ''))
  tiles = []
  for i in range(len(txt)):
    tiles.append(Tile.Tile(x+i*8, y, txt[i], size=1))
  return tiles
  
def _safeopen(fname):
  if not isinstance(fname, str):
    raise TypeError("Expected filename of type str")
  tree = None
  try:
    tree = et.parse(fname)
  except IOError as e:
    raise e
    
  return tree
      
  