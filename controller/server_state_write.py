import urwid

from controller.server_state import ServerState, BadReply, ServerStateMinibuf
import controller.server_state_waiting
from model.message import *

class ServerStateWrite(ServerStateMinibuf):
  def __init__(self, debugClient):
    ServerStateMinibuf.__init__(self, debugClient, u"Address data : ")
    # Memory request values
    self.address = 0
    self.data = 0
  def sendMemoryRequest(self):
    m = MessageMemoryWrite(self.address, self.data)
    self.debugClient.network.send(m)
    self.debugClient.addMessage(m)
  def onSubmit(self):
    self.sendMemoryRequest()
    self.changeState(ServerStateWriteReply)
  def validate(self):
    t = self.input.get_edit_text()
    t = t.rsplit(' ')
    if len(t) != 2:
      return 0
    self.address = int(t[0], 0)
    try:
      self.data = t[1].decode('hex')
    except:
      return 0
    return 1
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address, some data to write 0xffffffff 0x1000 and carriage return")

class ServerStateWriteReply(ServerState):
  def __init__(self, debugClient):
    self.debugClient = debugClient
  def notifyUserInput(self, input):
    self.usage()
  def notifyMessage(self, message):
    if not isinstance(message, MessageMemoryWriteCommit):
      raise BadReply
    self.debugClient.addMessage(message)
    self.changeState(controller.server_state_waiting.ServerStateWaiting)
  def usage(self):
    self.debugClient.gui.display("Usage()\n Waiting for the memory response")
