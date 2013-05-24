from controller.server_state import ServerStateReply
import controller.server_state_waiting
from model.message import *

class Command(object):
  def __init__(self):
    self.message = None
  def execute(self):
    raise NotImplementedError("Subclasses should implement this!")

class ServerStateCommand(ServerStateReply):
  def __init__(self, debugClient, command):
    ServerStateReply.__init__(self, debugClient)
    self.command = command
  def notifyMessage(self, message):
    # Execute command
    self.command.message = message
    if not self.command.execute():
      self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
    self.command.message = None
  def start(self):
    # Execute command
    if not self.command.execute():
      self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
