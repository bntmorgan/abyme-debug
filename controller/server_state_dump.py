from controller.server_state import ServerState, BadReply, ServerStateMinibuf
import controller.server_state_waiting
from model.message import *

class ServerStateDump(ServerStateMinibuf):
  def __init__(self, debugClient):
    ServerStateMinibuf.__init__(self, debugClient, u"Address length : ")
    # Memory request values
    self.address = 0
    self.length = 128
  def sendMemoryRequest(self):
    m = MessageMemoryRead(self.address, self.length)
    self.debugClient.network.send(m)
    self.debugClient.addMessage(m)
  def onCancel(self):
    self.changeState(controller.server_state_waiting.ServerStateWaiting)
  def onSubmit(self):
    self.sendMemoryRequest()
    self.changeState(ServerStateDumpReply)
  def validate(self):
    t = self.input.get_edit_text()
    t = t.rsplit(' ')
    if len(t) != 2:
      return 0
    self.address = int(t[0], 0)
    self.length = int(t[1], 0)
    return 1
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address and size 0xffffffff 0x1000 and carriage return")

class ServerStateDumpReply(ServerState):
  def __init__(self, debugClient):
    self.debugClient = debugClient
  def notifyUserInput(self, input):
    self.usage()
  def notifyMessage(self, message):
    if not isinstance(message, MessageMemoryData):
      raise BadReply
    self.debugClient.addMessage(message)
    self.changeState(controller.server_state_waiting.ServerStateWaiting)
  def usage(self):
    self.debugClient.gui.display("Usage()\n Waiting for the memory response")
