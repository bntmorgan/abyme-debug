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
  def execute(self):
    raise NotImplementedError("Subclasses should implement this!")
  def sendAndReceive(self, message, expected):
    self.messageOut = message
    self.expected = expected

class CommandMultiple(Command):
  def __init__(self, params, start):
    Command.__init__(self, params)
    # current
    self.current = start
  def execute(self):
    self.current()
  def next(self, next):
    self.current = next

class CommandMemoryRead(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.read)
  def read(self):
    self.sendAndReceive(MessageMemoryRead(self.params['address'], self.params['length']), MessageMemoryData)
    self.next(self.receive)
  def receive(self):
    self.params['memory'] = self.message.data

class CommandMemoryWrite(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.write)
  def write(self):
    self.sendAndReceive(MessageMemoryWrite(self.params['address'], self.params['memory']), MessageMemoryWriteCommit)
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
    self.sendAndReceive(MessageVMCSWrite(self.params['fields']), MessageVMCSWriteCommit)
    self.next(self.receive)
  def receive(self):
    self.params['ok'] = self.message.ok

class LinearToPhysical(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.getPagingMode)
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
  # Algorithm steps
  def checkPagingMode(self):
    self.IA32_EFER = self.params['fields']['GUEST_IA32_EFER'].value
    self.core = self.params['core']
    # Pagination activated ?
    if not (self.core.regs.cr0 & (1 << 0) and self.core.regs.cr0 & (1 << 31)):
      self.physical = self.linear
      # self.debugClient.info("Page Walk", "Pagination is not activated : %016x" % (self.physical))
      return
    # 32-Bit Paging
    elif not self.core.regs.cr4 & (1 << 5) and not self.IA32_EFER & (1 << 10):
      # self.debugClient.info("Page Walk", "Unsupported paging mode : 32-Bit Paging : %016x" % (self.physical))
      return
    # PAE Paging
    elif self.core.regs.cr4 & (1 << 5) and not self.IA32_EFER & (1 << 10):
      self.cr3 = self.core.regs.cr3 & 0x00000000fffffe00
      self.PDPTEAddress = self.cr3 | ((self.linear & 0xc0000000)>> 27)
      self.sendAndReceive(MessageMemoryRead(self.PDPTEAddress, 8), MessageMemoryData)
      self.next(self.getPDPTE)
    # IA-32e Paging
    elif self.core.regs.cr4 & (1 << 5) and self.IA32_EFER & (1 << 10):
      # self.debugClient.info("Page Walk", "Pagination is not activated : IA-32e Paging : %016x" % (self.physical))
      return
  # PDPTE
  def getPDPTE(self):
    self.PDPTE = unpack('Q', self.message.data)[0]
    # self.debugClient.info("Page Walk", "PDPTE : %016x" % (self.PDPTE))
    # Present ?
    if not (self.PDPTE & (1 << 0)):
      # self.debugClient.info("Page Walk", "Unsupported not present PDPTE")
      return
    self.PDEAddress = (self.PDPTE & 0x000ffffffffff000) | ((self.linear & 0x000000003fe00000) >> 18)
    self.sendAndReceive(MessageMemoryRead(self.PDEAddress, 8), MessageMemoryData)
    self.next(self.getPDE)
  # PDE
  def getPDE(self):
    self.PDE = unpack('Q', self.message.data)[0]
    # self.debugClient.info("Page Walk", "PDE : %016x" % (self.PDE))
    # Present and 2MB
    if not (self.PDE & 1):
      # self.debugClient.info("Page Walk", "Unsupported not present PDE")
      return
    elif (self.PDE & (1 << 0)) and (self.PDE & (1 << 7)):
      self.physical = (self.PTE & 0x000fffffffe00000) | (self.linear & 0x0000000001ffffc)
      # self.debugClient.info("Page Walk", "4MB page physical address : %016x" % (self.physical))
      return
    self.PTEAddress = (self.PDE & 0x000ffffffffff000) | ((self.linear & 0x00000000001ff000) >> 9)
    self.sendAndReceive(MessageMemoryRead(self.PTEAddress, 8), MessageMemoryData)
    self.next(self.getPTE)
  # PTE
  def getPTE(self):
    self.PTE = unpack('Q', self.message.data)[0]
    self.debugClient.info("Page Walk", "PTE : %016x" % (self.PTE))
    if not (self.PTE & 1):
      self.debugClient.info("Page Walk", "Unsupported not present")
      return
    self.physical = (self.PTE & 0x000ffffffffff000) | (self.linear & 0x000000000000ffc)
    # self.debugClient.info("Page Walk", "4Ko page physical address : %016x" % (self.physical))
    return

class MTF(Command):
  def __init__(self, params):
    Command.__init__(self, params)
    # mTF bit
    self.mTF = self.params['mTF']
    # Fields
    self.field = self.params['fields']['CPU_BASED_VM_EXEC_CONTROL']
    # current
    self.current = self.readPrimaryProcBasedVMExecControls
  # Algorithm steps
  def execute(self):
    self.field.value = (self.message.fields['CPU_BASED_VM_EXEC_CONTROL'].value & ((self.mTF << 27) | ~(1 << 27))) | (self.mTF << 27)
    self.params['fields']['CPU_BASE_VM_EXEC_CONTROL'].value = self.field.value
