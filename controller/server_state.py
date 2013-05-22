import urwid

class ServerState(object):
  def __init__(self):
    self.debugClient = None
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
    self.debugClient = debugClient
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

class ServerStateMinibufCommand(ServerStateMinibuf):
  def __init__(self, debugClient, label, command):
    ServerStateMinibuf.__init__(self, debugClient, label)
    self.command = command
  def submit(self):
    self.command.submit()
  def cancel(self):
    self.command.cancel()
  def validate(self, t):
    return self.command.validate(t)
  def usage(self):
    self.command.usage()
  def complete(self, t):
    self.command.complete(t)

class Command(object):
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
