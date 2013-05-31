from controller.command import *

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
    if self.commandFinished():
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
        self.command[0].message = None
        self.command[0].expected = None
        self.command[0].messageOut = None
  def send(self):
    self.debugClient.sendMessage(self.commands[0].messageOut)
  def isCommandNext(self):
    return len(self.commands) > 1
  def commandFinished(self):
    return self.commands[0].expected == None or self.commands[0].messageOut == None


