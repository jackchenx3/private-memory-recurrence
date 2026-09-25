"""Bounded4MiB record writer for separate true/observed query provenance.
Accepted I/O and its64MiB advisory-release behavior remain unchanged dependencies.
"""
import json
from io_utils import File as AcceptedFile
class File(AcceptedFile):
 def write(self,value):
  data=json.dumps(value,separators=(',',':'),allow_nan=False).encode()+b'\n'
  assert len(data)<4*1024*1024,'observation path exceeds bounded4MiB record cap'
  for start in range(0,len(data),1024*1024):self.z.write(data[start:start+1024*1024])
  self.release()
