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
  def changeState(self, serverStateClass):
    self.debugClient.serverState = serverStateClass(self.debugClient)

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
    self.addInput()
  def addInput(self):
    self.input = urwid.Edit(self.label, u"")
    self.bottomBar.contents.append((self.input, self.bottomBar.options()))
    urwid.connect_signal(self.input, "change", self.changed)
    self.bottomBar.focus_position = 2
  def removeInput(self):
    self.bottomBar.contents.pop()
  def onSubmit(self):
    raise NotImplementedError("Subclasses should implement this!")
  def notifyUserInput(self, input):
    if input == 'enter' and self.validate():
      self.removeInput()
      self.onSubmit()
    else:
      self.usage()
  def changed(self, widget, text):
    self.debugClient.gui.display('Typed : %s' % (text))
  def validate(self):
    raise NotImplementedError("Subclasses should implement this!")
  def notifyMessage(self, message):
    raise BadReply(-1)
  def usage(self):
    raise NotImplementedError("Subclasses should implement this!")
