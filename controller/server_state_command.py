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
  def submit(self):
    if self.command is not None:
      self.command.submit()
  def cancel(self):
    if self.command is not None:
      self.command.cancel()
  def validate(self, t):
    self.getCommand(t)
    if self.command is not None:
      return self.command.validate(self.args)
    else:
      return 0
  def complete(self, t):
    self.getCommand(t)
    if self.command is not None:
      self.command.complete(self.args)
    else:
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
