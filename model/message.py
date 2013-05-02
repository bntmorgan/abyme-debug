from struct import *

import socket, sys

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

'''
Input messages
'''

class MessageIn(Message):
  def __init__(self):
    super(MessageIn, self).__init__()
    # GUI
    self.new = 1
  @staticmethod
  def ethAddr (a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
    return b
  def format(self):
    n = "N" if self.new else " "
    l = "%04d B" % (self.frame.headerLength)
    # new length addrSource addrDest type
    return "%s %s %s %s" % (n, l, MessageIn.ethAddr(self.frame.macSource), MessageIn.ethAddr(self.frame.macDest))
  def pack(self):
    return pack('B', self.messageType)
  def unPack(self):
    t = unpack('!B', self.frame.payload[0])
    self.messageType = t[0]
  @staticmethod
  def createMessage(frame):
    # get the type of the message
    m = MessageIn();
    m.frame = frame
    m.unPack()
    # get the real message
    if m.messageType == Message.VMExit:
      m = MessageVMExit()
    #real unpack if changed
    m.frame = frame
    m.unPack()
    return m

class MessageVMExit(MessageIn):
  def __init__(self):
    super(MessageVMExit, self).__init__()
    self.messageType = Message.VMExit 
  def format(self):
    return "%s VMExit" % (super(MessageVMExit, self).format())

'''
Output messages
'''

class MessageOut(Message):
  def __init__(self):
    super(MessageOut, self).__init__()

class MessageExecContinue(MessageOut):
  def __init__(self):
    super(MessageExecContinue, self).__init__()
    self.messageType = Message.ExecContine

class MessageExecStep(MessageOut):
  def __init__(self):
    super(MessageExecContinue, self).__init__()
    self.messageType = Message.ExecStep
