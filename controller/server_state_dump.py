import urwid

from controller.server_state import ServerState, BadReply
import controller.server_state_waiting
from model.message import *

class ServerStateDump(ServerState):
  def __init__(self, debugClient):
    self.debugClient = debugClient
    self.bottomBar = self.debugClient.gui.bottomBar
    self.addInput()
    # Memory request values
    self.address = 0
    self.length = 128
  def addInput(self):
    self.address = urwid.Edit(u"Address length", u"")
    self.bottomBar.contents.append((self.address, self.bottomBar.options()))
    urwid.connect_signal(self.address, "change", self.addressChanged)
    self.bottomBar.focus_position = 2
  def removeInput(self):
    self.bottomBar.contents.pop()
  def notifyUserInput(self, input):
    if input == 'enter' and self.validate():
      self.removeInput()
      self.changeState(ServerStateDumpReply)
      self.sendMemoryRequest()
    else:
      self.usage()
  def addressChanged(self, widget, text):
    self.debugClient.gui.display('Typed : %s' % (text))
  def sendMemoryRequest(self):
    m = MessageMemoryRequest(self.address, self.length)
    self.network.send(m)
  def validate(self):
    t = self.address.get_edit_text()
    t = t.rsplit(' ')
    if len(t) != 2:
      return 0
    self.address = int(t[0], 0)
    self.length = int(t[1], 0)
    return 1
  def notifyMessage(self, message):
    raise BadReply(-1)
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address and size 0xffffffff 0x1000 and carriage return")

class ServerStateDumpReply(ServerState):
  def __init__(self, debugClient):
    self.debugClient = debugClient
  def notifyUserInput(self, input):
    self.usage()
  def notifyMessage(self, message):
    # format the resullllts
    self.debugClient.gui.display("Memory message received")
    self.changeState(controller.server_state_waiting.ServerStateWaiting)
  def usage(self):
    self.debugClient.gui.display("Usage()\n Waiting for the memory response")
