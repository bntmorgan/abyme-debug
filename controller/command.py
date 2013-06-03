from model.message import *

#
# The command object doesn't need to be interfaced with the 
# user only controller stuff
# I/O parameters are passed threw a dict
#

class Command(object):
  def __init__(self, params):
    # I/O Pameters
    self.params = params
    # Received message
    self.message = None
    # Message to send after execution
    self.messageOut = None
    # Class of the message to receive before the next execution
    self.expected = None
  def execute(self):
    raise NotImplementedError("Subclasses should implement this!")
  def sendAndReceive(self, message, expected):
    self.messageOut = message
    self.expected = expected

class CommandMultiple(Command):
  def __init__(self, params, start):
    Command.__init__(self, params)
    # current
    self.current = start
  def execute(self):
    self.current()
  def next(self, next):
    self.current = next

class CommandMemoryRead(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.read)
  def read(self):
    self.sendAndReceive(MessageMemoryRead(self.params['address'], self.params['length']), MessageMemoryData)
    self.next(self.receive)
  def receive(self):
    self.params['memory'] = self.message.data

class CommandMemoryWrite(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.write)
  def write(self):
    self.sendAndReceive(MessageMemoryWrite(self.params['address'], self.params['memory']), MessageMemoryWriteCommit)
    self.next(self.receive)
  def receive(self):
    self.params['ok'] = self.message.ok

class CommandCoreRegsRead(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.coreRegsRead)
  def coreRegsRead(self):
    self.sendAndReceive(MessageCoreRegsRead(), MessageCoreRegsData)
    self.next(self.receive)
  def receive(self):
    self.params['core'] = self.message.core

class CommandVMCSRead(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.vMCSRead)
  def vMCSRead(self):
    self.sendAndReceive(MessageVMCSRead(self.params['fields']), MessageVMCSData)
    self.next(self.receive)
  def receive(self):
    self.params['fields'] = self.message.fields

class CommandVMCSWrite(CommandMultiple):
  def __init__(self, params):
    CommandMultiple.__init__(self, params, self.vMCSWrite)
  def vMCSWrite(self):
    self.sendAndReceive(MessageVMCSWrite(self.params['fields']), MessageVMCSWriteCommit)
    self.next(self.receive)
  def receive(self):
    self.params['ok'] = self.message.ok
