from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Shell
import controller.server_state_waiting
import controller.server_state_set_line
import controller.server_state_dump
import controller.server_state_write
import controller.server_state_vmcs
import controller.linear_to_physical
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

class ServerStateShell(ServerStateMinibuf):
  def __init__(self, debugClient):
    ServerStateMinibuf.__init__(self, debugClient, u" : ")
    self.shell = None
    self.args = None
    # autocomplete
    self.cString = ''
    self.cValues = []
    self.cIndex = 0
    self.c = 0
  def submit(self):
    if self.shell is not None:
      self.shell.submit()
  def cancel(self):
    if self.shell is not None:
      self.shell.cancel()
    self.changeState(controller.server_state_waiting.ServerStateWaiting(self.debugClient))
    self.debugClient.gui.setMinibuf('')
  def validate(self, t):
    if self.c == 1:
      p = self.cString.split(" ")
      s = " ".join(p[:len(p) - 1]) + "%s%s " % ("" if len(self.cString) == 0 else " ", self.cValues[len(self.cValues) - 1 if self.cIndex == 0 else self.cIndex - 1])
      self.setText(s)
      self.cString = ''
      self.cValues = []
      self.cIndex = 0
      self.c = 0
      self.debugClient.gui.setMinibuf('')
    else:
      self.getShell(t)
      if self.shell is not None:
        return self.shell.validate(self.args)
      else:
        return 0
  def complete(self, t):
    if self.cString == t and len(self.cValues) > 0:
      self.debugClient.gui.setMinibuf(self.cValues[self.cIndex])
      self.cIndex = 0 if self.cIndex == len(self.cValues) - 1 else self.cIndex + 1
      self.c = 1
    else:
      self.cIndex = 0
      self.c = 0
      self.getShell(t)
      if self.shell is not None:
        self.cString = t
        self.cValues = self.shell.complete(self.args)
      else:
        self.cString = ""
        self.setText("")
        self.cValues = [
            "write",
            "read",
            "vmcs read",
            "walk",
            "<line>",
        ]
        self.usage()
  def usage(self):
    if self.shell is not None:
      self.shell.usage()
    else:
      self.debugClient.gui.display("write\nread\nvmcs read\nwalk\n<line>")
  def getShell(self, t):
    self.shell = None
    self.args = t
    test = TestRegex()
    if test.test("^[ ]*write (.*)$", t):
      self.shell = controller.server_state_write.ShellWrite(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^[ ]*read (.*)$", t):
      self.shell = controller.server_state_dump.ShellDump(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^[ ]*vmcs read (.*)$", t):
      self.shell = controller.server_state_vmcs.ShellVMCS(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^[ ]*walk (.*)$", t):
      self.shell = controller.linear_to_physical.ShellLinearToPhysical(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^.*[0-9]+.*$", t):
      self.shell = controller.server_state_set_line.ShellSetLine(self.debugClient)
    else:
      self.shell = None
