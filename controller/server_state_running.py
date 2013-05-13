import urwid

from controller.server_state import *
import controller.server_state_waiting

from model.message import *

class ServerStateRunning(ServerState):
  def __init__(self, debugClient):
    self.debugClient = debugClient
  def notifyUserInput(self, input):
    if input in ('q', 'Q'):
      raise urwid.ExitMainLoop()
    elif input == 'h':
      self.usage()
    elif input == 's':
      self.debugClient.setStep()
    else:
      self.usage()
  def notifyMessage(self, message):
    # Handle the message according to the type
    if message.messageType == Message.VMExit:
      # if we are not in step mode we directly continue the execution
      if self.debugClient.step:
        # Server is now waiting
        self.changeState(controller.server_state_waiting.ServerStateWaiting)
      else:
        self.debugClient.sendContinue()
    else:
      raise BadReply(message.messageType)
    # Adds here to the model and notifies the view of the changes
    self.debugClient.addMessage(message)
  def usage(self):
    self.debugClient.gui.display("Usage()\ns : Step execution\n")
