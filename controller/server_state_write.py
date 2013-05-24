import urwid

from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Shell, ServerStateReply
import controller.server_state_waiting
from model.message import *

class ShellWrite(Shell):
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
      self.data = t[1].decode('hex')
    except:
      return 0
    return 1
  def submit(self):
    self.sendMemoryRequest()
    self.changeState(ServerStateWriteReply(self.debugClient))
  def sendMemoryRequest(self):
    m = MessageMemoryWrite(self.address, self.data)
    self.debugClient.sendMessage(m)
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address, some data to write 0xffffffff 0x1000 and carriage return")

class ServerStateWriteReply(ServerStateReply):
  def notifyMessage(self, message):
    if not isinstance(message, MessageMemoryWriteCommit):
      raise BadReply
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
