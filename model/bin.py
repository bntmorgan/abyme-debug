import os, subprocess, tempfile
import string

from model.core import *

class Bin(object):
  def __init__(self, bin, address, mode):
    # code binary
    self.bin = bin
    # rip addres
    self.address = address
    # file passed to objdump
    self.file = None
    self.name = None
    # disasm code
    self.code = None
    # core mode
    self.mode = mode
  def __delete__(self):
    os.unlink(self.name)
  def mkTemp(self):
    if self.file is not None:
      return
    self.file = tempfile.NamedTemporaryFile(delete=False)
    self.name = file.name
    # write the bin into the file
    self.file.write(self.bin)
    # write the buffer into the file and close it
    self.file.close()
  def callObjdump(self):
    if self.code is not None:
      return
    if self.file is None:
      self.mkTemp()
    p = [
      'objdump',
      '-b', 'binary',
      '-mi386',
      '--adjust-vma', '0x%x' % (self.address),
      '-D', self.file.name,
    ]
    if self.mode == CoreMode.V8086 or self.mode == CoreMode.REAL:
      p.append('-Maddr16,data16')
    elif self.mode == CoreMode.PROTECTED:
      pass
      p.append('-Mi386')
    elif self.mode == CoreMode.IA32E:
      p.append('-Mx86-64')
    self.code = subprocess.check_output(p)
    self.code = filter(lambda x: (x in string.printable) and x != chr(9), self.code)
  def disasm(self):
    self.callObjdump()
    return self.code
