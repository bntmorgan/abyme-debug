import urwid

from server_state import ServerState

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
  def notifyMessage(self):
    self.debugClient.messages.append(message)
    message.number = self.debugClient.messages.length() - 1
    # Handle the message according to the type
    if message.messageType == Message.VMExit:
      # if we are not in step mode we directly continue the execution
      if self.step:
        # Server is now waiting
        self.changeState(ServerStateWaiting)
      else:
        self.debugClient.sendContinue()
    else:
      raise BadReply(message.messageType)
    # Adds here to the model and notifies the view of the changes
    self.debugClient.gui.notifyMessage(message)
    self.debugClient.messageFocus(message.number, message)
  def usage(self):
    self.debugClient.gui.display("Usage()\ns : Step execution\n")
