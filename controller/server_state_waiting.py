import urwid

from controller.server_state import ServerState, BadReply
import controller.server_state_running
import controller.server_state_dump

class ServerStateWaiting(ServerState):
  def __init__(self, debugClient):
    self.debugClient = debugClient
  def notifyUserInput(self, input):
    if input in ('q', 'Q'):
      raise urwid.ExitMainLoop()
    elif input == 'h':
      self.usage()
    elif input == 's':
      self.debugClient.setStep()
      self.debugClient.sendContinue()
      # server is now running
      self.changeState(controller.server_state_running.ServerStateRunning)
    elif input == 'c':
      self.debugClient.endStep()
      self.debugClient.sendContinue()
      # server is now running
      self.changeState(controller.server_state_running.ServerStateRunning)
    elif input == 't':
      if self.debugClient.mTF:
        self.debugClient.endMTF()
      else:
        self.debugClient.setMTF()
    elif input == 'd':
      self.changeState(controller.server_state_dump.ServerStateDump)
    else:
      self.usage()
  def notifyMessage(self, message):
    raise BadReply(-1)
  def usage(self):
    self.debugClient.gui.display("Usage()\ns : Step execution\nc : Continue execution\nh : Help\nt : Toggle monitor trap flag\nd : Dump memory")
