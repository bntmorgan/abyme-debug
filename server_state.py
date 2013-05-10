class ServerState(object):
  def __init__(self):
    self.debugClient = None
  def notifyUserInput(self, input):
    raise NotImplementedError("Subclasses should implement this!")
  def notifyMessage(self):
    raise NotImplementedError("Subclasses should implement this!")
  def usage(self):
    raise NotImplementedError("Subclasses should implement this!")
  def changeState(self, serverStateClass):
    self.debugClient.serverState = serverStateClass(self.debugClient)
