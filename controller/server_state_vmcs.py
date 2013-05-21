import urwid

from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Command
import controller.server_state_waiting
from model.message import *

class CommandVMCS(Command): 
  def __init__(self, debugClient):
    Command.__init__(self, debugClient)
    # autocomplete
    self.cString = ''
    self.cValues = []
    self.cIndex = 0
  def validate(self, t):
    return 1
  def cancel(self):
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
  def submit(self):
    self.sendVMCSRequest()
    # self.changeState(ServerStateWriteReply(self.debugClient))
  def sendVMCSRequest(self):
    self.usage()
  def complete(self, t):
    # autocomplete
    self.debugClient.gui.setMinibuf(self.cString)
    if self.cString == t and len(self.cValues) > 0:
      self.debugClient.gui.setMinibuf(self.cValues[self.cIndex])
      self.cIndex = 0 if self.cIndex >= len(self.cValues) else self.cIndex + 1
    else:
      self.cString = t
      self.cValues = []
      self.cIndex = 0
      # self.debugClient.vmcs.fields
      self.cValues = [k for k,v in self.debugClient.vmcs.fields.iteritems() if k.startswith(t)]
      s = ''
      for k in self.cValues:
        s = s + k + '\n'
      self.debugClient.gui.display(s)
  def usage(self):
    self.debugClient.gui.display("Usage()\n type a VMCS Field name and carriage return")
