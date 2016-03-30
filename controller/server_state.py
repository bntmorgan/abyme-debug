import urwid
import re
from collections import deque
from model.message import *
from model.bin import *
from controller.command import *
import log
import stat
import pickle
import os
from network import Network
from model.vmm import *

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
  @staticmethod
  def saveHistories():
    for cclass in ServerStateMinibuf.__subclasses__():
      # log.log(cclass.__name__)
      # log.log(cclass.history)
      try:
        pickle.dump(cclass.history, open(".history_%s" % (cclass.__name__), 'w'))
      except:
        pass
  @staticmethod
  def restoreHistories():
    for cclass in ServerStateMinibuf.__subclasses__():
      # log.log(cclass.__name__)
      try:
        cclass.history = pickle.load(open(".history_%s" % (cclass.__name__), 'r'))
      except:
        cclass.history = []
      # log.log(cclass.history)
  def __init__(self, debugClient, label):
    ServerState.__init__(self, debugClient)
    self.bottomBar = self.debugClient.gui.bottomBar
    self.label = label
    self.input = None
    self.addInput()
    self.historyPointer = 0
  def addInput(self):
    self.input = urwid.Edit(self.label, u"")
    self.bottomBar.contents.append((self.input, self.bottomBar.options()))
    # urwid.connect_signal(self.input, "change", self.changed)
    self.bottomBar.focus_position = 6
    self.debugClient.gui.focusMinibuf()
  def removeInput(self):
    self.bottomBar.contents.pop()
    self.debugClient.gui.focusList()
  def submit(self):
    raise NotImplementedError("Subclasses should implement this!")
  def cancel(self):
    raise NotImplementedError("Subclasses should implement this!")
  def getHistory(self):
    return self.__class__.history
  def getHistoryCMD(self):
    if len(self.getHistory()) > 0:
      self.input.set_edit_text(self.getHistory()[self.historyPointer])
      self.input.move_cursor_to_coords((len(self.input.get_edit_text()),), len(self.input.get_edit_text()), 1)
  def historyPush(self, cmd):
    self.getHistory().append(cmd)
  def historyBWD(self):
    if self.historyPointer == 0:
      self.historyPointer = len(self.getHistory()) - 1
    else:
      self.historyPointer = self.historyPointer - 1
    self.getHistoryCMD()
  def historyFWD(self):
    if self.historyPointer == len(self.getHistory()) - 1:
      self.historyPointer = 0
    else:
      self.historyPointer = self.historyPointer + 1
    self.getHistoryCMD()
  def notifyUserInput(self, input):
    if input == 'enter' and self.validate(self.input.get_edit_text()):
      self.removeInput()
      self.historyPush(self.input.get_edit_text())
      self.submit()
    elif input == 'esc':
      self.removeInput()
      self.cancel()
    elif input == 'tab':
      self.complete(self.input.get_edit_text())
    elif input == 'ctrl up':
      self.historyBWD()
    elif input == 'ctrl down':
      self.historyFWD()
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
  history = []
  def __init__(self, debugClient, label, shell):
    ServerStateMinibuf.__init__(self, debugClient, label)
    self.shell = shell
  def submit(self):
    self.shell.submit()
  def cancel(self):
    self.shell.cancel()
    self.changeState(ServerStateWaiting(self.debugClient))
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
  def cancel(self):
    raise NotImplementedError("Subclasses should implement this!")
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

# call wrapper for commands
# function reference and a list of parameters
def wrapper(func, args):
  func(*args)

class ServerStateNetboot(ServerStateReply):
  chunkSize = 0x400
  def __init__(self, debugClient, address):
    ServerStateReply.__init__(self, debugClient)
    #  XXX : Opens the efi image to netboot
    self.imagePath = "../uefi/binary/drivers/vmm_rec_0/efi.efi"
    self.size = os.path.getsize(self.imagePath)
    self.fd = open(self.imagePath, "rb")
    self.sent = 0
    self.sending = 0
    self.buf = None # Sending buffer
    self.address = address
  def notifyMessage(self, message):
    if not isinstance(message, MessageCommit):
      raise BadReply(self.command.message.messageType)
    if message.ok == 0:
      self.debugClient.info("Netboot failed", "failed to write in memory")
      self.changeState(ServerStateWaiting(self.debugClient))
      return
    if self.sending == 0: # Last write
      self.debugClient.info("Netboot succeed", "0x%08x bytes send" % (self.sent))
      self.changeState(ServerStateRunning(self.debugClient))
      return
    self.sent = self.sent + self.sending
    self.upload() # Uploading the rest of the file
  def upload(self):
    if self.sent == self.size: # end of file
      self.buf = ""
    else:
      self.buf = self.fd.read(ServerStateNetboot.chunkSize)
    self.sending = len(self.buf)
    self.mw = MessageMemoryWrite(self.address + self.sent, self.buf)
    log.log("uploading 0x%x bytes" % (self.sending))
    self.debugClient.sendMessage(self.mw)
    self.debugClient.info("Uploading %.2f %%" % ((self.sent * 1.) / self.size * 100), 
        "size(0x%08x)\n" % (self.size) +
        "sending(0x%08x)\n" % (self.sending) +
        "sent(0x%08x)\n" % (self.sent))

class ServerStateCommand(ServerStateReply):
  def __init__(self, debugClient, commands = [], params = {}, callback = None):
    ServerStateReply.__init__(self, debugClient)
    self.commands = deque(commands)
    self.callback = callback
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
      self.command.finished = True
      self.command.execute()
      if self.isCommandSend():
        self.send()
        self.command.message = None
        self.command.messageOut = None
      if self.isCommandExpected():
        self.command.expected = None
        break
      if self.isCommandFinished():
        if self.isCommandNext():
          self.commands.popleft()
          self.command = self.commands[0](self.params)
        else:
          # Finally finished : call the callback
          if (self.callback):
            wrapper(self.callback['f'], self.callback['p'])
          else: # Or go back to ServerStateWaiting
            self.changeState(ServerStateWaiting(self.debugClient))
          break
  def send(self):
    self.debugClient.sendMessage(self.command.messageOut)
  def isCommandNext(self):
    return len(self.commands) > 1
  def isCommandFinished(self):
    return self.command.finished
  def isCommandExpected(self):
    return self.command.expected != None
  def isCommandSend(self):
    return self.command.messageOut != None

class ShellRead(Shell):
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    # Memory request values
    self.address = 0
    self.length = 0
    self.filename = None
  def validate(self, t):
    t = t.rsplit(' ')
    if len(t) < 2:
      return 0
    try:
      self.address = int(t[0], 0)
      self.length = int(t[1], 0)
    except:
      return 0
    if len(t) == 3:
      self.filename = t[2]
    return 1
  def submit(self):
    s = ServerStateCommand(self.debugClient, [CommandMemoryRead],
      {'address': self.address, 'length': self.length, 'filename': self.filename})
    self.changeState(s)
    s.start()
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Type an address, size and filename if needed")
  def cancel(self):
    pass

class ShellReset(Shell):
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
  def validate(self, t):
    return 1
  def submit(self):
    self.debugClient.sendMessage(MessageReset())
    self.debugClient.endStep()
    s = ServerStateRunning(self.debugClient)
    self.changeState(s)
  def complete(self, t):
    self.usage()
    return []
  def usage(self):
    self.debugClient.gui.display("Usage()\n Carriage return !")
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
  def notifyMessage(self, message, bp = True):
    # Handle the message according to the type
    if message.messageType == Message.Netboot:
      # Server is now Netbootloading
      s = ServerStateNetboot(self.debugClient, 0xcafebabe)
      self.changeState(s)
      s.upload()
    elif message.messageType == Message.VMExit:
      # if we are not in step mode we directly continue the execution
      self.debugClient.vmm.set(self.debugClient.vmid, ExitReason.e[message.exitReason]['name'])
      if ExitReason.e[message.exitReason]['name'] == 'VMCALL':
        log.log("YES DUDES, THis is a VMCALL")
      elif self.debugClient.step:
        if self.debugClient.disass:
          s = ServerStateCommand(self.debugClient, [
            # Get IA32_EFER
            CommandVMCSRead,
            # Walks the address
            CommandWalkFromRIP,
            LinearToPhysical,
            # Write RIP for memory read
            CommandReadFromPhysical,
            # Memory read
            CommandMemoryRead,
            ], {
              'core' : self.debugClient.core,
              'vmid' : self.debugClient.vmid,
              'filename': None,
              'fields': {
                'GUEST_CS_BASE': self.debugClient.vmcs.fields['GUEST_CS_BASE']
                },
              })
          self.changeState(s)
          s.start()
        else: 
          # Server is now waiting
          self.changeState(ServerStateWaiting(self.debugClient))
      else:
        self.debugClient.sendContinue()
    # Demo EARS
    elif message.messageType == Message.UserDefined:
      if message.userType == MessageUserDefined.LogCR3:
        # Send to gui
        Network.sendTo(5000, message.data)
      elif message.userType == MessageUserDefined.LogMD5:
        # Send to gui
        Network.sendTo(5002, message.data)
      return
    elif message.messageType == Message.Info:
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
  history = []
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
            "vmexit",
            "reset",
            "<line>",
        ]
        self.usage()
  def usage(self):
    if self.shell is not None:
      self.shell.usage()
    else:
      self.debugClient.gui.display("write\nread\nvmcs read\nwalk\nvmexit\nreset\n<line>")
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
    elif test.test("^[ ]*reset$", t):
      self.shell = ShellReset(self.debugClient)
    elif test.test("^[ ]*vmexit (.*)$", t):
      self.shell = ShellSendDebug(self.debugClient)
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
    self.vmid = 0
    self.shadow = 0
  def validate(self, t):
    t = t.strip().rsplit(' ')
    try:
      self.f = self.debugClient.vmcs.fields[t[0].strip()]
    except:
      return 0
    if len(t) >= 2:
      try:
        self.vmid = int(t[1], 0)
      except:
        return 0
    else:
      self.vmid = self.debugClient.vmid
    if len(t) >= 3:
      if t[2] == 's':
        self.shadow = 1
      else:
        self.shadow = 0
    return 1
  def submit(self):
    s = ServerStateCommand(self.debugClient, [CommandVMCSRead],
        {'fields': {self.f.name : self.f}, 'vmid': self.vmid, 'shadow':
          self.shadow})
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

class ShellSendDebug(Shell):
  def __init__(self, debugClient):
    Shell.__init__(self, debugClient)
    self.r = None
    self.vmid = self.debugClient.vmid
    self.glbl = 0
  def validate(self, t):
    t = t.strip().split(' ');
    if len(t) >= 1:
      if (t[0].strip() == '*'):
        self.r = '*'
      elif (t[0].strip() == 'default'):
        self.r = 'default'
      elif (t[0].strip() == 'none'):
        self.r = 'none'
      else:
        try:
          # test the existance of the key
          tmp = self.debugClient.vmm.sendDebug[0][t[0].strip()]
          self.r = t[0].strip()
        except:
          return 0
    if len(t) >= 2:
      if (t[1].strip() == '*'):
        self.glbl = 1
      else:
        try:
          self.vmid = int(t[1], 0)
        except:
          return 0
    return 1
  def submit(self):
    # Handle submitted values
    log.log(self.glbl)
    log.log(self.vmid)
    if self.glbl:
      if self.r == '*':
        log.log("allGlbl")
        self.debugClient.vmm.setAllGlbl()
      elif self.r == 'default':
        self.debugClient.vmm.setDefaultGlbl()
      elif self.r == 'none':
        self.debugClient.vmm.setNoneGlbl()
      else:
        self.debugClient.vmm.toggleGlbl(self.r)
    else:
      if self.r == '*':
        log.log("all")
        self.debugClient.vmm.setAll(self.vmid)
      elif self.r == 'default':
        self.debugClient.vmm.setDefault(self.vmid)
      elif self.r == 'none':
        self.debugClient.vmm.setNone(self.vmid)
      else:
        self.debugClient.vmm.toggle(self.vmid, self.r)
    # Network command
    s = ServerStateCommand(self.debugClient, [CommandSendDebug],
        {'send_debug': self.debugClient.vmm.sendDebug, 'vmid': self.vmid})
    self.changeState(s)
    s.start()
  def complete(self, t):
    s = ''
    c = [k for k, v in self.debugClient.vmm.sendDebug[self.vmid].iteritems() if k.startswith(t)]
    if ('default'.startswith(t)):
      c.insert(0, 'default')
    if ('*'.startswith(t)):
      c.insert(0, '*')
    if ('none'.startswith(t)):
      c.insert(0, 'none')
    for k in c:
      try:
        k = k + ' (%d)' % (self.debugClient.vmm.sendDebug[self.vmid][k].active)
      except:
        pass
      s = s + k + '\n'
    self.debugClient.gui.display(s)
    return c
  def usage(self):
    self.debugClient.gui.display("Usage()\n type a VMExit reason name and carriage return")
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
    elif input == 'v':
      if self.debugClient.vPT:
        self.debugClient.endVPT()
      else:
        self.debugClient.setVPT()
      # Launch the command
      params = {
        'vPT': self.debugClient.vPT,
        'fields': {
          'PIN_BASED_VM_EXEC_CONTROL': self.debugClient.vmcs.fields['PIN_BASED_VM_EXEC_CONTROL'],
          'VM_EXIT_CONTROLS': self.debugClient.vmcs.fields['VM_EXIT_CONTROLS']
        }
      }
      s = ServerStateCommand(self.debugClient, [
        # Read Pin bases exec control VMCS field
        CommandVMCSRead,
        # Add or remove VPT flag
        VPT,
        # Add or remove VPT save on exit flag
        VPTSave,
        # Write Pin based exec control VMCS field
        CommandVMCSWrite
      ], params)
      self.changeState(s)
      s.start()
    elif input == 't':
      # Set / unset  senddebug for MTF and gui handling
      if self.debugClient.mTF:
        self.debugClient.endMTF()
        self.debugClient.vmm.unsetGlbl('MONITOR_TRAP_FLAG')
      else:
        self.debugClient.setMTF()
        self.debugClient.vmm.setGlbl('MONITOR_TRAP_FLAG')
      # Launch the command
      params = {
        'mTF': self.debugClient.mTF,
        'fields': {'CPU_BASED_VM_EXEC_CONTROL': self.debugClient.vmcs.fields['CPU_BASED_VM_EXEC_CONTROL']},
        'vmid': self.debugClient.vmid,
        'send_debug': self.debugClient.vmm.sendDebug
      }
      s = ServerStateCommand(self.debugClient, [
        # Read Proc based exec control VMCS field
        CommandVMCSRead,
        # Add or remove MTF flag
        MTF,
        # Write Proc based exec control VMCS field
        CommandVMCSWrite,
        # Update the vmexit server bitmap
        CommandSendDebug
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
      if self.debugClient.disass:
        self.debugClient.endDisass()
      else:
        self.debugClient.setDisass()
      if len(self.debugClient.messages) == 0:
        return
      self.debugClient.gui.listBoxModified()
    elif input == 'D':
      # Set disassemble mode
      self.debugClient.setDisass()
      # Launch the command
      s = ServerStateCommand(self.debugClient, [
        # Get IA32_EFER
        CommandVMCSRead,
        # Walks the address
        CommandWalkFromRIP,
        LinearToPhysical,
        # Write RIP for memory read
        CommandReadFromPhysical,
        # Memory read
        CommandMemoryRead,
        ], {
          'core': self.debugClient.core,
          'filename': None,
          'vmid': self.debugClient.vmid,
          'fields': {
            'GUEST_CS_BASE': self.debugClient.vmcs.fields['GUEST_CS_BASE']
          },
        })
      self.changeState(s)
      s.start()
    elif input == 'S':
      # Set disassemble mode
      self.debugClient.endDisass()
      # Launch the command
      s = ServerStateCommand(self.debugClient, [
        # Walks the address
        CommandWalkFromRSP,
        LinearToPhysical,
        # Write RSP for memory read
        CommandReadFromPhysical,
        # Memory read
        CommandMemoryRead,
        ], {
          'core': self.debugClient.core,
          'filename': None,
          'vmid': self.debugClient.vmid,
        })
      self.changeState(s)
      s.start()
    elif input == 'p':
      if len(self.debugClient.messages) == 0:
        return
      self.debugClient.gui.listBoxModified()
    elif input == ':':
      self.changeState(ServerStateShell(self.debugClient))
    elif input == 'R':
      s = ServerStateCommand(self.debugClient, [CommandCoreRegsRead],
        {'core': Core()})
      self.changeState(s)
      s.start()
    else:
      self.usage()
  def notifyMessage(self, message):
    self.debugClient.info("Debug Client resetted", "Debug Client has been resetted. The host has rebooted or this is maybe a serious bug dude :(")
    ServerStateRunning.notifyMessage(ServerStateRunning(self.debugClient), message)
    # raise BadReply(-1)
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
d : Try to disassemble data
D : Try to disassemble from RIP
S : Dump the stack of the current VM
p : Print raw message dat
R : Print the regs
q : Quit
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
      {'address': self.address, 'data': self.data, 'ok': 0})
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
      'core': Core(),
      'vmid': self.debugClient.vmid,
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
