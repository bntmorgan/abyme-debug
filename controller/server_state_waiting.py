import urwid

from controller.server_state import ServerState, BadReply, ServerStateMinibufShell
import controller.server_state_running
import controller.server_state_dump
import controller.server_state_write
import controller.server_state_set_line
import controller.server_state_regs
import controller.server_state_shell
import model.message
from model.bin import Bin

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
      self.changeState(controller.server_state_running.ServerStateRunning(self.debugClient))
    elif input == 'up':
      self.debugClient.gui.messageFocusDec()
    elif input == 'down':
      self.debugClient.gui.messageFocusInc()
    elif input == 'c':
      self.debugClient.endStep()
      self.debugClient.sendContinue()
      # server is now running
      self.changeState(controller.server_state_running.ServerStateRunning(self.debugClient))
    elif input == 't':
      if self.debugClient.mTF:
        self.debugClient.endMTF()
      else:
        self.debugClient.setMTF()
    elif input == 'r':
      self.changeState(ServerStateMinibufShell(self.debugClient, 
        u"Address length : ",
        controller.server_state_dump.ShellDump(self.debugClient)))
    elif input == 'w':
      self.changeState(ServerStateMinibufShell(self.debugClient, 
        u"Address data : ",
        controller.server_state_write.ShellWrite(self.debugClient)))
    elif input == 'd':
      if len(self.debugClient.messages) == 0:
        return
      m = self.debugClient.messages[self.debugClient.gui.listBox.focus_position]
      if isinstance(m, model.message.MessageMemoryData):
        b = Bin(m.data, 0)
        self.debugClient.gui.display(b.disasm())
        b = None
    elif input == 'p':
      if len(self.debugClient.messages) == 0:
        return
      m = self.debugClient.messages[self.debugClient.gui.listBox.focus_position]
      self.debugClient.gui.display(m.formatFull())
    elif input == ':':
      self.changeState(controller.server_state_shell.ServerStateShell(self.debugClient))
    elif input == 'R':
      self.changeState(controller.server_state_regs.ServerStateRegs(self.debugClient))
    else:
      self.usage()
  def notifyMessage(self, message):
    raise BadReply(-1)
  def usage(self):
    self.debugClient.gui.display("Usage()\ns : Step execution\nc : Continue execution\nh : Help\nt : Toggle monitor trap flag\nr : Dump memory\nw : Write memory\nd : try to disassemble data\np : print raw message data\nR : Print the regs")
