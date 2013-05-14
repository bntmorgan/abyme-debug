import urwid

from controller.server_state import ServerState, BadReply
import controller.server_state_running
import controller.server_state_dump
import controller.server_state_write
import controller.server_state_set_line

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
    elif input == 'up':
      self.debugClient.gui.messageFocusDec()
    elif input == 'down':
      self.debugClient.gui.messageFocusInc()
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
    elif input == 'r':
      self.changeState(controller.server_state_dump.ServerStateDump)
    elif input == 'w':
      self.changeState(controller.server_state_write.ServerStateWrite)
    elif input == ':':
      self.changeState(controller.server_state_set_line.ServerStateSetLine)
    else:
      self.usage()
  def notifyMessage(self, message):
    raise BadReply(-1)
  def usage(self):
    self.debugClient.gui.display("Usage()\ns : Step execution\nc : Continue execution\nh : Help\nt : Toggle monitor trap flag\nr : Dump memory\nw : Write memory")
