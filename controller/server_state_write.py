import urwid

from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Command
import controller.server_state_waiting
from model.message import *

class CommandWrite(Command):
  def __init__(self, debugClient):
    Command.__init__(self, debugClient)
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
  def cancel(self):
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
  def submit(self):
    self.sendMemoryRequest()
    self.changeState(ServerStateWriteReply(self.debugClient))
  def sendMemoryRequest(self):
    m = MessageMemoryWrite(self.address, self.data)
    self.debugClient.network.send(m)
    self.debugClient.addMessage(m)
  def complete(self, t):
    self.usage()
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
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
  def usage(self):
    self.debugClient.gui.display("Usage()\n Waiting for the memory response")
