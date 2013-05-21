from controller.server_state import ServerState, BadReply, ServerStateMinibuf, Command
import controller.server_state_waiting
import controller.server_state_set_line
import controller.server_state_dump
import controller.server_state_write
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
    self.command = controller.server_state_set_line.CommandSetLine(self.debugClient)
  def submit(self):
    self.command.submit()
  def cancel(self):
    self.command.cancel()
  def validate(self, t):
    test = TestRegex()
    if test.test("^[ ]*write (.*)$", t):
      self.command = controller.server_state_write.CommandWrite(self.debugClient)
      t = test.m.group(1)
    elif test.test("^[ ]*read (.*)$", t):
      self.command = controller.server_state_dump.CommandDump(self.debugClient)
      t = test.m.group(1)
    else:
      self.command = controller.server_state_set_line.CommandSetLine(self.debugClient)
    return self.command.validate(t)
  def usage(self):
    self.command.usage()
