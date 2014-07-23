import urwid
import re
from collections import deque
from model.message import *
from model.bin import *
from controller.command import *
import log

class ServerState(object):
  def __init__(self, debugClient):
    self.debugClient = debugClient
  def notifyUserInput(self, input):
    raise NotImplementedError("Subclasses should implement this!")
  def notifyMessage(self, message):
    raise NotImplementedError("Subclasses should implement this!")
  def usage(self):
    raise NotImplementedError("Subclasses should implement this!")
  def changeState(self, serverState):
    log.log("%s --> %s" % (self.__class__.__name__, serverState.__class__.__name__))
    self.debugClient.serverState = serverState

class BadReply(BaseException):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Unexpected reply message type : %d " % (self.value)

class ServerStateMinibuf(ServerState):
  def __init__(self, debugClient, label):
    ServerState.__init__(self, debugClient)
    self.bottomBar = self.debugClient.gui.bottomBar
    self.label = label
    self.input = None
    self.addInput()
  def addInput(self):
    self.input = urwid.Edit(self.label, u"")
    self.bottomBar.contents.append((self.input, self.bottomBar.options()))
    # urwid.connect_signal(self.input, "change", self.changed)
    self.bottomBar.focus_position = 2
    self.debugClient.gui.focusMinibuf()
  def removeInput(self):
    self.bottomBar.contents.pop()
    self.debugClient.gui.focusList()
  def submit(self):
    raise NotImplementedError("Subclasses should implement this!")
  def cancel(self):
    raise NotImplementedError("Subclasses should implement this!")
  def notifyUserInput(self, input):
    if input == 'enter' and self.validate(self.input.get_edit_text()):
      self.removeInput()
      self.submit()
    elif input == 'esc':
      self.removeInput()
      self.cancel()
    elif input == 'tab':
      self.complete(self.input.get_edit_text())
    else:
      self.usage()
  def changed(self, widget, text):
    self.debugClient.gui.display('Typed : %s' % (text))
  def setText(self, t):
    self.input.set_edit_text(t)
    self.input.set_edit_pos(len(t))
  def validate(self, t):
    raise NotImplementedError("Subclasses should implement this!")
  def complete(self, t):
    raise NotImplementedError("Subclasses should implement this!")
  def notifyMessage(self, message):
    sys.exit(0xf0f0)
    raise BadReply(-1)
  def usage(self):
    raise NotImplementedError("Subclasses should implement this!")

class ServerStateMinibufShell(ServerStateMinibuf):
  def __init__(self, debugClient, label, shell):
    ServerStateMinibuf.__init__(self, debugClient, label)
    self.shell = shell
  def submit(self):
    self.shell.submit()
  def cancel(self):
    self.shell.cancel()
  def validate(self, t):
    return self.shell.validate(t)
  def usage(self):
    self.shell.usage()
  def complete(self, t):
    self.shell.complete(t)

class Shell(object):
  def __init__(self, debugClient):
    self.debugClient = debugClient
  def validate(self, t):
    raise NotImplementedError("Subclasses should implement this!")
  # def cancel(self):
    # raise NotImplementedError("Subclasses should implement this!")
  def submit(self):
    raise NotImplementedError("Subclasses should implement this!")
  def usage(self):
    raise NotImplementedError("Subclasses should implement this!")
  def complete(self, t):
    raise NotImplementedError("Subclasses should implement this!")
  def changeState(self, state):
    self.debugClient.serverState.changeState(state)

class ServerStateReply(ServerState):
  def __init__(self, debugClient):
    ServerState.__init__(self, debugClient)
  def notifyUserInput(self, input):
    if (input == 'esc'):
      self.changeState(ServerStateWaiting(self.debugClient))
    else:
      self.usage()
  def usage(self):
    self.debugClient.gui.display("Usage()\n Waiting for response... Press escape to stop")

class ServerStateCommand(ServerStateReply):
  def __init__(self, debugClient, commands = [], params = {}):
    ServerStateReply.__init__(self, debugClient)
    self.commands = deque(commands)
    # Partage du debugClient aux commandes
    params['debugClient'] = debugClient
    self.params = params
    self.comand = None
  def notifyMessage(self, message):
    self.command.message = message
    if self.command.expected != None and not isinstance(self.command.message, self.command.expected):
      raise BadReply(self.command.message.messageType)
    # Execute and handle the commands
    self.execute()
  def start(self):
    # Execute and handle the commands
    self.command = self.commands[0](self.params)
    self.execute()
  def execute(self):
    while 1:
      self.command.execute()
      if self.commandFinished():
        if self.isCommandNext():
          self.commands.popleft()
          self.command = self.commands[0](self.params)
        else:
          # Finally finished
          self.changeState(ServerStateWaiting(self.debugClient))
          break
      else:
        self.send()
        self.command.message = None
        self.command.expected = None
        self.command.messageOut = None
        break
  def send(self):
    self.debugClient.sendMessage(self.command.messageOut)
  def isCommandNext(self):
    return len(self.commands) > 1
  def commandFinished(self):
    return self.command.expected == None or self.command.messageOut == None

class ShellRead(Shell):
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    # Memory request values
    self.address = 0
    self.length = 0
  def validate(self, t):
    t = t.rsplit(' ')
    if len(t) != 2:
      return 0
    try:
      self.address = int(t[0], 0)
      self.length = int(t[1], 0)
    except:
      return 0
    return 1
  def submit(self):
    s = ServerStateCommand(self.debugClient, [CommandMemoryRead],
      {'address': self.address, 'length': self.length, 'memory': None})
    self.changeState(s)
    s.start()
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address and size 0xffffffff 0x1000 and carriage return")
  def cancel(self):
    pass

class ServerStateRunning(ServerState):
  def __init__(self, debugClient):
    ServerState.__init__(self, debugClient)
  def notifyUserInput(self, input):
    if input in ('q', 'Q'):
      raise urwid.ExitMainLoop()
    elif input == 'h':
      self.usage()
    elif input == 's':
      self.debugClient.setStep()
    elif input == 'f':
      self.changeState(ServerStateWaiting(self.debugClient))
    elif input == 'up':
      self.debugClient.gui.messageFocusDec()
    elif input == 'down':
      self.debugClient.gui.messageFocusInc()
    else:
      self.usage()
  def notifyMessage(self, message):
    # Handle the message according to the type
    if message.messageType == Message.UnhandledVMExit:
      ## self.debugClient.setStep()
      # Server is now waiting
      ## self.changeState(ServerStateWaiting(self.debugClient))
      self.debugClient.sendContinue()
    elif message.messageType == Message.VMExit:
      # if we are not in step mode we directly continue the execution
      if self.debugClient.step:
        # Server is now waiting
        self.changeState(ServerStateWaiting(self.debugClient))
      else:
        self.debugClient.sendContinue()
    elif message.messageType == Message.VMMPanic:
      self.debugClient.setStep()
      self.changeState(ServerStateWaiting(self.debugClient))
    elif message.messageType == Message.LogCR3:
      # self.debugClient.sendContinue()
      return
    elif message.messageType == Message.Info:
      # self.debugClient.sendContinue()
      return
    else:
      raise BadReply(message.messageType)
  def usage(self):
    self.debugClient.gui.display("Usage()\nq : Quit\ns : Step execution\nf : Force waiting state (if VMM already waiting)")

class ShellSetLine(Shell):
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    self.line = 0
  def validate(self, t):
    try:
      self.line = int(t)
    except:
      return 0
    return 1
  def submit(self):
    # set line
    self.debugClient.gui.messageFocus(self.line)
    self.changeState(ServerStateWaiting(self.debugClient))
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type a number a line")
  def cancel(self):
    pass

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
    self.changeState(ServerStateWaiting(self.debugClient))
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
      self.shell = ShellWrite(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^[ ]*read (.*)$", t):
      self.shell = ShellRead(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^[ ]*vmcs read (.*)$", t):
      self.shell = ShellVMCS(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^[ ]*walk (.*)$", t):
      self.shell = ShellLinearToPhysical(self.debugClient)
      self.args = test.m.group(1)
    elif test.test("^.*[0-9]+.*$", t):
      self.shell = ShellSetLine(self.debugClient)
    else:
      self.shell = None

class ShellVMCS(Shell): 
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    self.f = None
  def validate(self, t):
    try:
      self.f = self.debugClient.vmcs.fields[t.strip()]
    except:
      return 0
    return 1
  def submit(self):
    s = ServerStateCommand(self.debugClient, [CommandVMCSRead],
      {'fields': {self.f.name : self.f}})
    self.changeState(s)
    s.start()
  def complete(self, t):
    # self.debugClient.vmcs.fields
    c = [k for k, v in self.debugClient.vmcs.fields.iteritems() if k.startswith(t)]
    s = ''
    for k in c:
      s = s + k + '\n'
    self.debugClient.gui.display(s)
    return c
  def usage(self):
    self.debugClient.gui.display("Usage()\n type a VMCS Field name and carriage return")
  def cancel(self):
    pass

class ServerStateWaiting(ServerState):
  def __init__(self, debugClient):
    ServerState.__init__(self, debugClient)
  def notifyUserInput(self, input):
    if input in ('q', 'Q'):
      raise urwid.ExitMainLoop()
    elif input == 'h':
      self.usage()
    elif input == 's':
      self.debugClient.setStep()
      self.debugClient.sendContinue()
      # server is now running
      self.changeState(ServerStateRunning(self.debugClient))
    elif input == 'up':
      self.debugClient.gui.messageFocusDec()
    elif input == 'down':
      self.debugClient.gui.messageFocusInc()
    elif input == 'c':
      self.debugClient.endStep()
      self.debugClient.sendContinue()
      # server is now running
      self.changeState(ServerStateRunning(self.debugClient))
      # Expire the cache
      self.debugClient.cacheExpired()
    elif input == 'v':
      if self.debugClient.vPT:
        self.debugClient.endVPT()
      else:
        self.debugClient.setVPT()
      # Launch the command
      params = {
        'vPT': self.debugClient.vPT,
        'fields': {'PIN_BASED_VM_EXEC_CONTROL': self.debugClient.vmcs.fields['PIN_BASED_VM_EXEC_CONTROL']}
      }
      s = ServerStateCommand(self.debugClient, [
        # Read Pin bases exec control VMCS field
        CommandVMCSRead,
        # Add or remove VPT flag
        VPT,
        # Write Pin based exec control VMCS field
        CommandVMCSWrite
      ], params)
      self.changeState(s)
      s.start()
    elif input == 't':
      if self.debugClient.mTF:
        self.debugClient.endMTF()
      else:
        self.debugClient.setMTF()
      # Launch the command
      params = {
        'mTF': self.debugClient.mTF,
        'fields': {'CPU_BASED_VM_EXEC_CONTROL': self.debugClient.vmcs.fields['CPU_BASED_VM_EXEC_CONTROL']}
      }
      s = ServerStateCommand(self.debugClient, [
        # Read Proc based exec control VMCS field
        CommandVMCSRead,
        # Add or remove MTF flag
        MTF,
        # Write Proc based exec control VMCS field
        CommandVMCSWrite
      ], params)
      self.changeState(s)
      s.start()
    elif input == 'r':
      self.changeState(ServerStateMinibufShell(self.debugClient, 
        u"Address length : ",
        ShellRead(self.debugClient)))
    elif input == 'w':
      self.changeState(ServerStateMinibufShell(self.debugClient, 
        u"Address data : ",
        ShellWrite(self.debugClient)))
    elif input == 'd':
      if len(self.debugClient.messages) == 0:
        return
      m = self.debugClient.messages[self.debugClient.gui.listBox.focus_position]
      if isinstance(m, MessageMemoryData):
        b = Bin(m.data, 0)
        self.debugClient.gui.display(b.disasm())
        b = None
    elif input == 'p':
      if len(self.debugClient.messages) == 0:
        return
      m = self.debugClient.messages[self.debugClient.gui.listBox.focus_position]
      self.debugClient.gui.display(m.formatFull())
    elif input == ':':
      self.changeState(ServerStateShell(self.debugClient))
    elif input == 'R':
      s = ServerStateCommand(self.debugClient, [CommandCoreRegsRead],
        {'core': None})
      self.changeState(s)
      s.start()
    else:
      self.usage()
  def notifyMessage(self, message):
    raise BadReply(-1)
  def usage(self):
    self.debugClient.gui.display("""\
Usage()
s : Step execution
c : Continue execution
h : Help
t : Toggle monitor trap flag
v : Toggle VMX preemption timer
r : Dump memory
w : Write memory
d : try to disassemble data
p : print raw message dat
R : Print the regs
""")

class ShellWrite(Shell):
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    # Memory request values
    self.address = 0
    self.length = 0
    self.data = None
  def validate(self, t):
    t = t.rsplit(' ')
    if len(t) != 2:
      return 0
    try:
      self.address = int(t[0], 0)
      self.data = t[1].decode('hex')
    except:
      return 0
    return 1
  def submit(self):
    s = ServerStateCommand(self.debugClient, [CommandMemoryWrite],
      {'address': self.address, 'memory': self.data, 'ok': 0})
    self.changeState(s)
    s.start()
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address, some data to write 0xffffffff 0x1000 and carriage return")
  def cancel(self):
    pass

class ShellLinearToPhysical(Shell): 
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    self.linear = 0x0
  def validate(self, t):
    try:
      self.linear = int(t, 0)
    except:
      return 0
    return 1
  def submit(self):
    params = {
      'core': None,
      'fields': {'GUEST_IA32_EFER': self.debugClient.vmcs.fields['GUEST_IA32_EFER']},
      'linear': self.linear
    }
    s = ServerStateCommand(self.debugClient, [
      # Get core regs
      CommandCoreRegsRead,
      # Get IA32_EFER
      CommandVMCSRead,
      # Do the page walk
      LinearToPhysical
    ], params)
    self.changeState(s)
    s.start()
  def complete(self, t):
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n type an address and a carriage return")
  def cancel(self):
    pass

class ServerStatePanic(ServerState):
  def __init__(self, debugClient):
    ServerState.__init__(self, debugClient)
  def notifyUserInput(self, input):
    if input in ('q', 'Q'):
      raise urwid.ExitMainLoop()
    elif input == 'h':
      self.usage()
    elif input == 'f':
      self.changeState(ServerStateWaiting(self.debugClient))
    else:
      self.usage()
  def usage(self):
    self.debugClient.gui.display("Usage()\nq : Quit\nf : Force waiting state (if VMM rebooted)")
