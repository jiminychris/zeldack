class Portal(object):
  def __init__(self, destfile, destx, desty):
    self._destfile = destfile
    self._destx = destx
    self._desty = desty
    
  @property
  def destfile(self):
    return self._destfile
  @property
  def destx(self):
    return self._destx
  @property
  def desty(self):
    return self._desty