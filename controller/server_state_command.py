from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Command
import controller.server_state_waiting
import controller.server_state_set_line
import controller.server_state_dump
import controller.server_state_write
import controller.server_state_vmcs
import re
from model.message import *

class TestRegex(object):
  def __init__(self):
    self.p = None
    self.t = None
    self.m = None
  def test(self, p, t):
    self.p = p
    self.t = t
    self.m = re.match(p, t)
    return self.m

class ServerStateCommand(ServerStateMinibuf):
  def __init__(self, debugClient):
    ServerStateMinibuf.__init__(self, debugClient, u" : ")
    self.command = None
    self.args = None
    # autocomplete
    self.cString = ''
    self.cValues = []
    self.cIndex = 0
    self.c = 0
  def submit(self):
    if self.command is not None:
      self.command.submit()
  def cancel(self):
    if self.command is not None:
      self.command.cancel()
    else:
      self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
    self.debugClient.gui.setMinibuf('')
  def validate(self, t):
    if self.c == 1:
      p = self.cString.split(" ")
      s = " ".join(p[:len(p) - 1]) + " %s " % (self.cValues[len(self.cValues) - 1 if self.cIndex == 0 else self.cIndex - 1])
      self.setText(s)
      self.cString = ''
      self.cValues = []
      self.cIndex = 0
      self.c = 0
      self.debugClient.gui.setMinibuf('')
    else:
      self.getCommand(t)
      if self.command is not None:
        return self.command.validate(self.args)
      else:
        return 0
  def complete(self, t):
    if self.cString == t and len(self.cValues) > 0:
      self.debugClient.gui.setMinibuf(self.cValues[self.cIndex])
      self.cIndex = 0 if self.cIndex == len(self.cValues) - 1 else self.cIndex + 1
      self.c = 1
    else:
      self.cString = t
      self.cIndex = 0
      self.c = 0
      self.getCommand(t)
      if self.command is not None:
        self.cValues = self.command.complete(self.args)
      else:
        self.cValues = [
            "write",
            "read",
            "vmcs read",
            "<line>",
        ]
        self.usage()
  def usage(self):
    if self.command is not None:
      self.command.usage()
    else:
      self.debugClient.gui.display("write\nread\nvmcs read\n<line>")
  def getCommand(self, t):
    self.command = None
    self.args = t
    test = TestRegex()
    if test.test("^[ ]*write (.*)$", t):
      self.command = controller.server_state_write.CommandWrite(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^[ ]*read (.*)$", t):
      self.command = controller.server_state_dump.CommandDump(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^[ ]*vmcs read (.*)$", t):
      self.command = controller.server_state_vmcs.CommandVMCS(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^.*[0-9]+.*$", t):
      self.command = controller.server_state_set_line.CommandSetLine(self.debugClient)
    else:
      self.command = None
