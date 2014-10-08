from model.message import *

#
# The command object doesn't need to be interfaced with the
# user only controller stuff
# I/O parameters are passed threw a dict
#

class Command(object):
  def __init__(self, params):
    # I/O Pameters
    self.params = params
    # Received message
    self.message = None
    # Message to send after execution
    self.messageOut = None
    # Class of the message to receive before the next execution
    self.expected = None
    # Command finished ?
    self.finished = False
  def execute(self):
    raise NotImplementedError("Subclasses should implement this!")
  def sendAndReceive(self, message, expected):
    self.messageOut = message
    self.expected = expected
    self.finished = False
  def info(self, label, text):
    if self.params['debugClient']:
      self.params['debugClient'].info(label, text)

class CommandMultiple(Command):
  def __init__(self, params, start):
    Command.__init__(self, params)
    # current
    self.current = start
  def execute(self):
    self.current()
  def next(self, next):
    self.current = next
    self.finished = False

class CommandMemoryRead(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.read)
    self.cAddress = self.params['address']
    self.tLen = self.params['length']
    self.cLen = 0x0 
    if self.params['filename'] != None:
      try:
        self.file = open(self.params['filename'], "w")
      except:
        self.file = None
    else:
      self.file = None
  def read(self):
    # self.info("CommandMemoryRead : read", "cLen %d" % self.cLen)
    l = 0x400 if 0x400 < self.tLen - self.cLen else self.tLen - self.cLen 
    self.sendAndReceive(MessageMemoryRead(self.cAddress, l), MessageMemoryData)
    self.cLen = self.cLen + l
    self.cAddress = self.cAddress + l
    self.next(self.receive)
  def receive(self):
    # self.info("CommandMemoryRead : receive", "cLen %d" % self.cLen)
    if self.file != None:
      self.file.write(self.message.data)
      self.file.flush()
    if (self.cLen == self.tLen):
      if self.file != None:
        self.file.close()
    else:
      self.next(self.read)

class CommandMemoryWrite(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.write)
  def write(self):
    self.sendAndReceive(MessageMemoryWrite(self.params['address'], self.params['memory']), MessageCommit)
    self.next(self.receive)
  def receive(self):
    self.params['ok'] = self.message.ok

class CommandCoreRegsRead(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.coreRegsRead)
  def coreRegsRead(self):
    self.sendAndReceive(MessageCoreRegsRead(), MessageCoreRegsData)
    self.next(self.receive)
  def receive(self):
    self.params['core'] = self.message.core

class CommandReadFromRIP(Command):
  def __init__(self, params):
    Command.__init__(self, params)
  def execute(self):
    self.params['address'] = self.params['core'].regs.rip
    self.params['length'] = 0x100

class CommandVMCSRead(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.vMCSRead)
  def vMCSRead(self):
    self.sendAndReceive(MessageVMCSRead(self.params['fields']), MessageVMCSData)
    self.next(self.receive)
  def receive(self):
    self.params['fields'] = self.message.fields

class CommandVMCSWrite(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.vMCSWrite)
  def vMCSWrite(self):
    self.sendAndReceive(MessageVMCSWrite(self.params['fields']), MessageCommit)
    self.next(self.receive)
  def receive(self):
    self.params['ok'] = self.message.ok

class LinearToPhysical(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.checkPagingMode)
    # The address to convert
    self.linear = self.params['linear']
    # The result
    self.physical = 0
    # Algorithm data
    self.core = None
    self.IA32_EFER = None
    self.cr3 = 0
    self.PDPTEAddress = 0
    self.PDPTE = 0
    self.PDEAddress = 0
    self.PDE = 0
    self.PTEAddress = 0
    self.PTE = 0
    # For IA-32e Paging
    self.PML4EAddress = 0
    self.PML4E = 0
  # Algorithm steps
  def checkPagingMode(self):
    self.IA32_EFER = self.params['fields']['GUEST_IA32_EFER'].value
    self.core = self.params['core']
    # Pagination activated ?
    if not (self.core.regs.cr0 & (1 << 0) and self.core.regs.cr0 & (1 << 31)):
      self.physical = self.linear
      self.info("Page Walk", "Pagination is not activated : %016x" % (self.physical))
      return
    # 32-Bit Paging
    elif not self.core.regs.cr4 & (1 << 5) and not self.IA32_EFER & (1 << 10):
      self.info("Page Walk", "Unsupported paging mode : 32-Bit Paging : %016x" % (self.physical))
      return
    # PAE Paging
    elif self.core.regs.cr4 & (1 << 5) and not self.IA32_EFER & (1 << 10):
      self.cr3 = self.core.regs.cr3 & 0x00000000fffffe00
      self.PDPTEAddress = self.cr3 | ((self.linear & 0xc0000000)>> 27)
      self.sendAndReceive(MessageMemoryRead(self.PDPTEAddress, 8), MessageMemoryData)
      self.next(self.getPDPTE)
    # IA-32e Paging
    elif self.core.regs.cr4 & (1 << 5) and self.IA32_EFER & (1 << 10):
      # MAXPHYADDR = at most 52
      self.cr3 = self.core.regs.cr3 & 0x000ffffffffff000
      self.PML4EAddress = self.cr3 | ((self.linear >> 36) & (0x1ff << 3))
      self.info("Page Walk", "PML4EAddr : %016x" % (self.PML4EAddress))
      self.sendAndReceive(MessageMemoryRead(self.PML4EAddress, 8), MessageMemoryData)
      self.next(self.getPML4E)
  # PML4E
  def getPML4E(self):
    self.PML4E = unpack('Q', self.message.data)[0]
    self.info("Page Walk", "PML4E : %016x" % (self.PML4E))
    if not (self.PML4E & (1 << 0)):
      self.info("Page Walk", "Unsupported not present PML4E")
    else:
      self.PDPTEAddress = (self.PML4E & 0x000ffffffffff000) | ((self.linear >> 27) & (0x1ff << 3))
      self.info("Page Walk", "PDPTEAddr : %016x" % (self.PDPTEAddress))
      self.sendAndReceive(MessageMemoryRead(self.PDPTEAddress, 8), MessageMemoryData)
      self.next(self.getPDPTE)
  # PDPTE
  def getPDPTE(self):
    self.PDPTE = unpack('Q', self.message.data)[0]
    self.info("Page Walk", "PDPTE : %016x" % (self.PDPTE))
    if not (self.PDPTE & (1 << 0)):
      self.info("Page Walk", "Unsupported not present PDPTE")
    elif self.PDPTE & (1 << 7): # Page present
      self.physical = (self.PDPTE & 0x000fffffc0000000) | (self.linear & 0x000000003fffffff)
      self.info("Page Walk", "1GB page physical address : %016x" % (self.physical))
    else:
      self.PDEAddress = (self.PDPTE & 0x000ffffffffff000) | ((self.linear >> 18) & (0x1ff << 3))
      self.info("Page Walk", "PDEAddr : %016x" % (self.PDEAddress))
      self.sendAndReceive(MessageMemoryRead(self.PDEAddress, 8), MessageMemoryData)
      self.next(self.getPDE)
  # PDE
  def getPDE(self):
    self.PDE = unpack('Q', self.message.data)[0]
    self.info("Page Walk", "PDE : %016x" % (self.PDE))
    if not (self.PDE & (1 << 0)):
      self.info("Page Walk", "Unsupported not present PDE")
    elif self.PDE & (1 << 7): # Page present
      self.physical = (self.PDE & 0x000fffffffe00000) | (self.linear & 0x00000000001fffff)
      self.info("Page Walk", "2MB page physical address : %016x" % (self.physical))
    else:
      self.PTEAddress = (self.PDE & 0x000ffffffffff000) | ((self.linear >> 9) & (0x1ff << 3))
      self.info("Page Walk", "PTEAddr : %016x" % (self.PTEAddress))
      self.sendAndReceive(MessageMemoryRead(self.PTEAddress, 8), MessageMemoryData)
      self.next(self.getPTE)
  # PTE
  def getPTE(self):
    self.PTE = unpack('Q', self.message.data)[0]
    self.info("Page Walk", "PTE : %016x" % (self.PTE))
    if not (self.PTE & (1 << 0)):
      self.info("Page Walk", "Unsupported not present PTE")
    else:
      self.physical = (self.PTE & 0x000ffffffffff000) + (self.linear & 0x0000000000000fff)
      self.info("Page Walk", "4KB page physical address : %016x" % (self.physical))

class MTF(Command):
  def __init__(self, params):
    Command.__init__(self, params)
    # mTF bit
    self.mTF = self.params['mTF']
    # Fields
    self.field = self.params['fields']['CPU_BASED_VM_EXEC_CONTROL']
  # Algorithm steps
  def execute(self):
    self.field.value = (self.field.value & ((self.mTF << 27) | ~(1 << 27))) | (self.mTF << 27)
    self.params['fields']['CPU_BASED_VM_EXEC_CONTROL'].value = self.field.value

class VPT(Command):
  def __init__(self, params):
    Command.__init__(self, params)
    # vPT bit
    self.vPT = self.params['vPT']
    # Fields
    self.field = self.params['fields']['PIN_BASED_VM_EXEC_CONTROL']
  # Algorithm steps
  def execute(self):
    self.field.value = (self.field.value & ((self.vPT << 6) | ~(1 << 6))) | (self.vPT << 6)
    self.params['fields']['PIN_BASED_VM_EXEC_CONTROL'].value = self.field.value

class VPTSave(Command):
  def __init__(self, params):
    Command.__init__(self, params)
    # vPT bit
    self.vPT = self.params['vPT']
    # Fields
    self.field = self.params['fields']['VM_EXIT_CONTROLS']
  # Algorithm steps
  def execute(self):
    self.field.value = (self.field.value & ((self.vPT << 22) | ~(1 << 22))) | (self.vPT << 22)
    self.params['fields']['VM_EXIT_CONTROLS'].value = self.field.value

class IOBitmaps(Command):
  def __init__(self, params):
    Command.__init__(self, params)
    # mTF bit
    self.mTF = self.params['iOBitmaps']
    # Fields
    self.field = self.params['fields']['CPU_BASED_VM_EXEC_CONTROL']
  # Algorithm steps
  def execute(self):
    self.field.value = (self.field.value & ((self.mTF << 25) | ~(1 << 25))) | (self.mTF << 25)
    self.params['fields']['CPU_BASED_VM_EXEC_CONTROL'].value = self.field.value
