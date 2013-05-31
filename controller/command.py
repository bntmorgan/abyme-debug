from model.message import *

#
# The command object doesn't need to be interfaced with the 
# user only controller stuff
#

class Command(object):
  def __init__(self):
    self.message = None
    # message to send after execution
    self.messageOut = None
    # Class of the message to receive before the next execution
    self.expected = None
  def execute(self):
    raise NotImplementedError("Subclasses should implement this!")
  def sendAndReceive(message, expected):
    self.messageOut = message
    self.expected = expected

class CommandMultiple(Command):
  def __init__(self):
    Command.__init__(self, start)
    # current
    self.current = start
  def execute(self):
    self.current()
  def next(self, next):
    self.current = next

class CommandMemoryRead(CommandMultiple):
  def __init__(self, address, length, memory):
    CommandMultiple.__init__(self, self.read)
    # I
    self.address = address
    self.length = length
    # O
    self.memory = memory
  def read(self):
    self.sendAndReceive(MessageMemoryRead(self.address, self.length), MessageMemoryData)
    self.next(self.receive)
  def receive(self):
    self.memory = self.message.data

class CommandMemoryWrite(CommandMultiple):
  def __init__(self, address, memory, ok):
    CommandMultiple.__init__(self, self.write)
    # I
    self.address = address
    self.memory = memory
    # O
    self.ok = ok
  def write(self):
    self.sendAndReceive(MessageMemoryWrite(self.address, self.memory), MessageMemoryWriteCommit)
    self.next(self.receive)
  def receive(self):
    self.ok = self.message.ok

class CommandCoreRegsRead(CommandMultiple):
  def __init__(self, core):
    CommandMultiple.__init__(self, self.coreRegsRead)
    # I
    # O
    self.core = core
  def coreRegsRead(self):
    self.sendAndReceive(MessageCoreRegsRead(), MessageCoreRegsData)
    self.next(self.receive)
  def receive(self):
    self.core = self.message.core

class CommandVMCSRead(CommandMultiple):
  def __init__(self, fields):
    CommandMultiple.__init__(self, self.vMCSRead)
    # I/O
    self.fields = fields
  def vMCSRead(self):
    self.sendAndReceive(MessageVMCSRead(self.fields), MessageVMCSData)
    self.next(self.receive)
  def receive(self):
    self.fields = self.message.fields

class CommandVMCSWrite(CommandMultiple):
  def __init__(self, fields, ok):
    CommandMultiple.__init__(self, self.vMCSWrite)
    # I/O
    self.fields = fields
  def vMCSWrite(self):
    self.sendAndReceive(MessageVMCSWrite(self.fields), MessageVMCSWriteCommit)
    self.next(self.receive)
  def receive(self):
    self.ok = self.message.ok
