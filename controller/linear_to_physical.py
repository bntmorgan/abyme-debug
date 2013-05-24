from controller.server_state_command import ServerStateCommand, Command
from controller.server_state import Shell
from network import Network
from model.message import *

class ShellLinearToPhysical(Shell): 
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    self.linear = 0x0
  def validate(self, t):
    try:
      self.linear = int(t, 0)
    except:
      return 0
    return 1
  def submit(self):
    s = ServerStateCommand(self.debugClient, LinearToPhysical(self.linear, self.debugClient))
    self.changeState(s)
    s.start()
  def complete(self, t):
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n type an address and a carriage return")

class LinearToPhysical(Command):
  def __init__(self, linear, debugClient):
    Command.__init__(self)
    self.debugClient = debugClient
    # The address to convert
    self.linear = linear
    # The result
    self.physical = 0x0
    # Current step of the algorithm
    self.current = self.getCore
    # Algorithm data
    self.core = None
    self.IA32_EFER = None
  # Algorithm steps
  def getCore(self):
    m = MessageCoreRegsRead()
    self.debugClient.sendMessage(m)
    self.current = self.getIA32_EFER
    return 1
  def getIA32_EFER(self):
    self.core = self.message.core
    m = MessageVMCSRead([self.debugClient.vmcs.fields['GUEST_IA32_EFER']])
    self.debugClient.sendMessage(m)
    self.current = self.checkPagingMode
    return 1
  def checkPagingMode(self):
    self.IA32_EFER = self.message.fields['GUEST_IA32_EFER'].value
    if not (self.core.regs.cr0 & (1 << 0) and self.core.regs.cr0 (1 << 31)):
      self.physical = self.linear
      self.debugClient.info("Page Walk", "Pagination is not activated : %016x" % (self.physical))
      return 0
    return self.getCore()
  # Result
  def getPhysical(self):
    return self.physical
  # Execution
  def execute(self):
    return self.current()
