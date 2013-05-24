from controller.server_state import ServerState, BadReply, ServerStateMinibuf
import controller.server_state_waiting
from model.message import *

class ServerStateRegs(ServerStateReply):
  def __init__(self, debugClient):
    ServerStateReply.__init__(self, debugClient)
    self.sendRegsRequest()
  def sendRegsRequest(self):
    m = MessageCoreRegsRead()
    self.debugClient.network.send(m)
    self.debugClient.addMessage(m)
  def notifyMessage(self, message):
    if not isinstance(message, MessageCoreRegsData):
      raise BadReply
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
