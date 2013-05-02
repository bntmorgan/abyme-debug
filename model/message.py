from struct import *

import socket, sys

class Message():
  # Message Types
  (
      VMExit,
      ExecContinue,
      ExecStep,
  ) = range(3)
  def __init__(self):
    self.messageType = 0
  def pack(self):
    return pack('B', self.messageType)

'''
Input messages
'''

class MessageIn(Message):
  def __init__(self):
    super(MessageIn, self).__init__()
    # Debug protocol XXX
    self.messageType = 0
    # GUI
    self.new = 1
  @staticmethod
  def ethAddr (a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
    return b
  def format(self):
    n = "N" if self.new else " "
    t = "VM exit"
    l = "%04d B" % (self.frame.headerLength)
    # new length addrSource addrDest type
    return "%s %s %s %s %s" % (n, l, Message.ethAddr(self.frame.macSource), Message.ethAddr(self.frame.macDest), t)
  @staticmethod
  def createMessage(frame):
    m = MessageVMExit()
    m.frame = frame
    return m

class MessageVMExit(MessageIn):
  def __init__(self):
    super(MessageVMExit, self).__init__()
    self.messageType = Message.VMExit 

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
