import os, subprocess, tempfile

class Bin(object):
  def __init__(self, bin, address):
    # code binary
    self.bin = bin
    # rip addres
    self.address = address
    # file passed to objdump
    self.file = None
    self.name = None
    # disasm code
    self.code = None
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
    self.code = subprocess.check_output([
      'objdump',
      '-b', 'binary',
      '-mi386',
      '--adjust-vma', '0x%x' % (self.address),
      '-Mx86-64',
      #'-Maddr16,data16',
      '-D', self.file.name,
    ])
  def disasm(self):
    self.callObjdump()
    return self.code
