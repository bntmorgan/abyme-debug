from struct import *

import socket, sys

'''
Message collection
'''
class Messages(object):
  def __init__(self):
    self.messages = [];
  def append(self, message):
    self.messages.append(message)
  def length(self):
    return len(self.messages)

'''
Message
'''

class Message(object):
  # Message Types
  (
      Message,
      VMExit,
      ExecContinue,
      ExecStep,
  ) = range(4)
  def __init__(self):
    self.messageType = Message.Message
  def unPack(self):
    t = unpack('B', self.frame.payload[0])
    self.messageType = t[0]
  def pack(self):
    return pack('B', self.messageType)
  @staticmethod
  def createMessage(frame):
    # get the type of the message
    m = MessageIn();
    m.frame = frame
    m.unPack()
    # get the real message
    if m.messageType == Message.VMExit:
      m = MessageVMExit()
    elif m.messageType == Message.ExecContinue:
      m = MessageExecContinue()
    elif m.messageType == Message.ExecStep:
      m = MessageExecStep()
    #real unpack if changed
    m.frame = frame
    m.unPack()
    return m

'''
Input messages
'''

class MessageIn(Message):
  def __init__(self):
    super(MessageIn, self).__init__()
    # GUI
    self.new = 1
    self.number = 0
  @staticmethod
  def ethAddr (a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
    return b
  def format(self):
    n = "N" if self.new else " "
    n = "N" if self.new else " "
    l = "%04d B" % (self.frame.headerLength)
    # new length addrSource addrDest type
    return "%04d %s %s %s %s" % (self.number, n, l, MessageIn.ethAddr(self.frame.macSource), MessageIn.ethAddr(self.frame.macDest))
  def formatFull(self):
    n = "N" if self.new else " "
    l = "%04d B" % (self.frame.headerLength)
    # new length addrSource addrDest type
    return "number : %04d\nnew : %s\nheader length : %s\nsrc address : %s\ndest address : %s" % (self.number, n, l, MessageIn.ethAddr(self.frame.macSource), MessageIn.ethAddr(self.frame.macDest))

class MessageVMExit(MessageIn):
  def __init__(self):
    super(MessageVMExit, self).__init__()
    self.messageType = Message.VMExit 
    self.exitReason = 0xff
  def format(self):
    return "%s VMExit" % (super(MessageVMExit, self).format())
  def unPack(self):
    t = unpack('B', self.frame.payload[0])
    self.messageType = t[0]
    t = unpack('I', self.frame.payload[1:5])
    self.exitReason = t[0]
  def pack(self):
    return pack('BI', self.messageType, self.exitReason)
  def formatFull(self):
    return super(MessageVMExit, self).formatFull() + "\nexit reason : 0x%x (%d)" % (self.exitReason, self.exitReason & 0xffff)

'''
Output messages
'''

class MessageOut(Message):
  def __init__(self):
    super(MessageOut, self).__init__()

class MessageExecContinue(MessageOut):
  def __init__(self):
    super(MessageExecContinue, self).__init__()
    self.messageType = Message.ExecContinue

class MessageExecStep(MessageOut):
  def __init__(self):
    super(MessageExecContinue, self).__init__()
    self.messageType = Message.ExecStep
