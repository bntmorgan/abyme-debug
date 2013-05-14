from controller.server_state import ServerState, BadReply, ServerStateMinibuf
import controller.server_state_waiting
from model.message import *

class ServerStateSetLine(ServerStateMinibuf):
  def __init__(self, debugClient):
    ServerStateMinibuf.__init__(self, debugClient, u": ")
    self.line = 0
  def onSubmit(self):
    # set line
    self.debugClient.gui.messageFocus(self.line)
    self.changeState(controller.server_state_waiting.ServerStateWaiting)
  def validate(self):
    t = self.input.get_edit_text()
    try:
      self.line = int(t)
    except:
      return 0
    return 1
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type a number a line")
