from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Shell, ServerStateReply
import controller.server_state_waiting
from model.message import *

class ShellDump(Shell):
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    # Memory request values
    self.address = 0
    self.length = 0
  def validate(self, t):
    t = t.rsplit(' ')
    if len(t) != 2:
      return 0
    try:
      self.address = int(t[0], 0)
      self.length = int(t[1], 0)
    except:
      return
    return 1
  def cancel(self):
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
  def submit(self):
    self.sendMemoryRequest()
    self.changeState(ServerStateDumpReply(self.debugClient))
  def sendMemoryRequest(self):
    m = MessageMemoryRead(self.address, self.length)
    self.debugClient.network.send(m)
    self.debugClient.addMessage(m)
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address and size 0xffffffff 0x1000 and carriage return")

class ServerStateDumpReply(ServerStateReply):
  def notifyMessage(self, message):
    if not isinstance(message, MessageMemoryData):
      raise BadReply
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
