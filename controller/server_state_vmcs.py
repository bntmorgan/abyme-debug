import urwid

from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Command
import controller.server_state_waiting
from model.message import *

class CommandVMCS(Command): 
  def __init__(self, debugClient):
    Command.__init__(self, debugClient)
    self.f = None
  def validate(self, t):
    try:
      self.f = self.debugClient.vmcs.fields[t.strip()]
    except:
      return 0
    return 1
  def cancel(self):
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
  def submit(self):
    self.sendVMCSRequest()
    self.changeState(ServerStateVMCSReadReply(self.debugClient))
  def sendVMCSRequest(self):
    m = MessageVMCSRead([self.f])
    self.debugClient.network.send(m)
    self.debugClient.addMessage(m)
  def complete(self, t):
    # self.debugClient.vmcs.fields
    c = [k for k, v in self.debugClient.vmcs.fields.iteritems() if k.startswith(t)]
    s = ''
    for k in c:
      s = s + k + '\n'
    self.debugClient.gui.display(s)
    return c
  def usage(self):
    self.debugClient.gui.display("Usage()\n type a VMCS Field name and carriage return")

class ServerStateVMCSReadReply(ServerState):
  def __init__(self, debugClient):
    self.debugClient = debugClient
  def notifyUserInput(self, input):
    self.usage()
  def notifyMessage(self, message):
    if not isinstance(message, MessageVMCSData):
      raise BadReply
    self.debugClient.addMessage(message)
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
  def usage(self):
    self.debugClient.gui.display("Usage()\n Waiting for the VMCS Fields response")
