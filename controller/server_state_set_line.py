from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Shell
import controller.server_state_waiting
from model.message import *

class ShellSetLine(Shell):
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    self.line = 0
  def validate(self, t):
    try:
      self.line = int(t)
    except:
      return 0
    return 1
  def cancel(self):
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
  def submit(self):
    # set line
    self.debugClient.gui.messageFocus(self.line)
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type a number a line")
