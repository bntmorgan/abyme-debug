import urwid
import re
from model.message import *
from model.bin import *
from controller.command import *

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
  def __init__(self, debugClient, commands = []):
    ServerStateReply.__init__(self, debugClient)
    self.commands = commands
  def notifyMessage(self, message):
    self.commands[0].message = message
    if self.commands[0].expected != None and not isinstance(self.commands[0].message, self.commands[0].expected):
      raise BadReply(self.commands[0].message.messageType)
    # Execute and handle the commands
    self.execute()
  def start(self):
    # Execute and handle the commands
    self.execute()
  def execute(self):
    while 1:
      self.commands[0].execute()
      if self.commandFinished():
        if self.isCommandNext():
          self.commands.pop()
        else:
          # Finally finished
          self.changeState(ServerStateWaiting(self.debugClient))
          break
      else:
        self.send()
        self.commands[0].message = None
        self.commands[0].expected = None
        self.commands[0].messageOut = None
        break
  def send(self):
    self.debugClient.sendMessage(self.commands[0].messageOut)
  def isCommandNext(self):
    return len(self.commands) > 1
  def commandFinished(self):
    return self.commands[0].expected == None or self.commands[0].messageOut == None

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
    s = ServerStateCommand(self.debugClient, [
      CommandMemoryRead({'address': self.address, 'length': self.length, 'memory': None})])
    self.changeState(s)
    s.start()
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address and size 0xffffffff 0x1000 and carriage return")

class ServerStateDumpReply(ServerStateReply):
  def notifyMessage(self, message):
    if not isinstance(message, MessageMemoryData):
      raise BadReply(message.messageType)
    self.changeState(ServerStateWaiting(self.debugClient))

class ServerStateRegs(ServerStateReply):
  def __init__(self, debugClient):
    ServerStateReply.__init__(self, debugClient)
    self.sendRegsRequest()
  def sendRegsRequest(self):
    m = MessageCoreRegsRead()
    self.debugClient.sendMessage(m)
  def notifyMessage(self, message):
    if not isinstance(message, MessageCoreRegsData):
      raise BadReply(message.messageType)
    self.changeState(ServerStateWaiting(self.debugClient))
    # Install the core object into debug client
    self.debugClient.core = message.core

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
    else:
      self.usage()
  def notifyMessage(self, message):
    # Handle the message according to the type
    if message.messageType == Message.UnhandledVMExit:
      self.debugClient.setStep()
      # Server is now waiting
      self.changeState(ServerStateWaiting(self.debugClient))
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
      # self.changeState(ServerStatePanic(self.debugClient))
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
    self.sendVMCSRequest()
    self.changeState(ServerStateVMCSReadReply(self.debugClient))
  def sendVMCSRequest(self):
    m = MessageVMCSRead([self.f])
    self.debugClient.sendMessage(m)
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

class ServerStateVMCSReadReply(ServerStateReply):
  def notifyMessage(self, message):
    if not isinstance(message, MessageVMCSData):
      raise BadReply
    self.changeState(ServerStateWaiting(self.debugClient))
    # Cache the received fields into debugClient
    for f in message.fields:
      self.debugClient.vmcs.fields[f.name] = f

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
    elif input == 't':
      if self.debugClient.mTF:
        self.debugClient.endMTF()
      else:
        self.debugClient.setMTF()
      # Launch the command
      s = ServerStateCommand(self.debugClient, MTF(self.debugClient.mTF, self.debugClient))
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
      self.changeState(ServerStateRegs(self.debugClient))
    else:
      self.usage()
  def notifyMessage(self, message):
    raise BadReply(-1)
  def usage(self):
    self.debugClient.gui.display("Usage()\ns : Step execution\nc : Continue execution\nh : Help\nt : Toggle monitor trap flag\nr : Dump memory\nw : Write memory\nd : try to disassemble data\np : print raw message data\nR : Print the regs")

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
    self.sendMemoryRequest()
    self.changeState(ServerStateWriteReply(self.debugClient))
  def sendMemoryRequest(self):
    m = MessageMemoryWrite(self.address, self.data)
    self.debugClient.sendMessage(m)
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address, some data to write 0xffffffff 0x1000 and carriage return")

class ServerStateWriteReply(ServerStateReply):
  def notifyMessage(self, message):
    if not isinstance(message, MessageMemoryWriteCommit):
      raise BadReply
    self.changeState(ServerStateWaiting(self.debugClient))

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
    s = ServerStateCommand(self.debugClient, LinearToPhysical(self.linear, self.debugClient))
    self.changeState(s)
    s.start()
  def complete(self, t):
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n type an address and a carriage return")

class LinearToPhysical(Command):
  def __init__(self, linear, debugClient):
    Command.__init__(self)
    self.debugClient = debugClient
    # The address to convert
    self.linear = linear
    # The result
    self.physical = 0
    # Current step of the algorithm
    self.current = self.getCore
    # Algorithm data
    self.core = None
    self.IA32_EFER = None
    self.cr3 = 0
    self.PDPTEAddress = 0
    self.PDPTE = 0
    self.PDEAddress = 0
    self.PDE = 0
    self.PTEAddress = 0
    self.PTE = 0
  # Algorithm steps
  def getCore(self):
    m = MessageCoreRegsRead()
    self.debugClient.sendMessage(m)
    self.current = self.getIA32_EFER
    self.expected = MessageCoreRegsData
    return 1
  def getIA32_EFER(self):
    self.core = self.message.core
    m = MessageVMCSRead([self.debugClient.vmcs.fields['GUEST_IA32_EFER']])
    self.debugClient.sendMessage(m)
    self.current = self.checkPagingMode
    self.expected = MessageVMCSData
    return 1
  def checkPagingMode(self):
    self.IA32_EFER = self.message.fields['GUEST_IA32_EFER'].value
    # Pagination activated ?
    if not (self.core.regs.cr0 & (1 << 0) and self.core.regs.cr0 & (1 << 31)):
      self.physical = self.linear
      self.debugClient.info("Page Walk", "Pagination is not activated : %016x" % (self.physical))
      return 0
    # 32-Bit Paging
    elif not self.core.regs.cr4 & (1 << 5) and not self.IA32_EFER & (1 << 10):
      self.debugClient.info("Page Walk", "Unsupported paging mode : 32-Bit Paging : %016x" % (self.physical))
      return 0
    # PAE Paging
    elif self.core.regs.cr4 & (1 << 5) and not self.IA32_EFER & (1 << 10):
      self.cr3 = self.core.regs.cr3 & 0x00000000fffffe00
      self.PDPTEAddress = self.cr3 | ((self.linear & 0xc0000000)>> 27)
      m = MessageMemoryRead(self.PDPTEAddress, 8)
      self.debugClient.sendMessage(m)
      self.current = self.getPDPTE
      self.expected = MessageMemoryData
      return 1
    # IA-32e Paging
    elif self.core.regs.cr4 & (1 << 5) and self.IA32_EFER & (1 << 10):
      self.debugClient.info("Page Walk", "Pagination is not activated : IA-32e Paging : %016x" % (self.physical))
      return 0
  # PDPTE
  def getPDPTE(self):
    self.PDPTE = unpack('Q', self.message.data)[0]
    self.debugClient.info("Page Walk", "PDPTE : %016x" % (self.PDPTE))
    # Present ?
    if not (self.PDPTE & (1 << 0)):
      self.debugClient.info("Page Walk", "Unsupported not present PDPTE")
      return 0
    self.PDEAddress = (self.PDPTE & 0x000ffffffffff000) | ((self.linear & 0x000000003fe00000) >> 18)
    m = MessageMemoryRead(self.PDEAddress, 8)
    self.debugClient.sendMessage(m)
    self.current = self.getPDE
    self.expected = MessageMemoryData
    return 1
  # PDE
  def getPDE(self):
    self.PDE = unpack('Q', self.message.data)[0]
    self.debugClient.info("Page Walk", "PDE : %016x" % (self.PDE))
    # Present and 2MB
    if not (self.PDE & 1):
      self.debugClient.info("Page Walk", "Unsupported not present PDE")
      return 0
    elif (self.PDE & (1 << 0)) and (self.PDE & (1 << 7)):
      self.physical = (self.PTE & 0x000fffffffe00000) | (self.linear & 0x0000000001ffffc)
      self.debugClient.info("Page Walk", "4MB page physical address : %016x" % (self.physical))
      return 0
    self.PTEAddress = (self.PDE & 0x000ffffffffff000) | ((self.linear & 0x00000000001ff000) >> 9)
    m = MessageMemoryRead(self.PTEAddress, 8)
    self.debugClient.sendMessage(m)
    self.current = self.getPTE
    self.expected = MessageMemoryData
    return 1
  # PTE
  def getPTE(self):
    self.PTE = unpack('Q', self.message.data)[0]
    self.debugClient.info("Page Walk", "PTE : %016x" % (self.PTE))
    if not (self.PTE & 1):
      self.debugClient.info("Page Walk", "Unsupported not present")
    self.physical = (self.PTE & 0x000ffffffffff000) | (self.linear & 0x000000000000ffc)
    self.debugClient.info("Page Walk", "4Ko page physical address : %016x" % (self.physical))
    return 0
  # Result
  def getPhysical(self):
    return self.physical
  # Execution
  def execute(self):
    return self.current()

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

class MTF(Command):
  def __init__(self, mTF, debugClient):
    Command.__init__(self)
    self.debugClient = debugClient
    # mTF bit
    self.mTF = mTF
    # Fields
    self.field = self.debugClient.vmcs.fields['CPU_BASED_VM_EXEC_CONTROL']
    # current
    self.current = self.readPrimaryProcBasedVMExecControls
  # Algorithm steps
  def readPrimaryProcBasedVMExecControls(self):
    m = MessageVMCSRead([self.field])
    self.debugClient.sendMessage(m)
    self.current = self.writePrimaryProcBasedVMExecControls
    self.expected = MessageVMCSData
    return 1
  def writePrimaryProcBasedVMExecControls(self):
    self.field.value = (self.message.fields['CPU_BASED_VM_EXEC_CONTROL'].value & ((self.mTF << 27) | ~(1 << 27))) | (self.mTF << 27)
    # self.field.value = self.message.fields['CPU_BASED_VM_EXEC_CONTROL'].value
    m = MessageVMCSWrite([self.field])
    self.debugClient.sendMessage(m)
    self.current = self.writeCommit
    self.expected = MessageVMCSWriteCommit
    return 1
  def writeCommit(self):
    return 0
  # Execution
  def execute(self):
    return self.current()
