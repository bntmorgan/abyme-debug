from struct import *

import socket, sys, math

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
      MemoryRead,
      MemoryData
  ) = range(6)
  def __init__(self):
    self.messageType = Message.Message
    self.core = 0
  def unPack(self):
    t = unpack('BB', self.frame.payload[0:2])
    self.messageType = t[0]
    self.core = t[1]
  def pack(self):
    return pack('BB', self.messageType, self.core)
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
    elif m.messageType == Message.MemoryRead:
      m = MessageMemoryRead()
    elif m.messageType == Message.MemoryData:
      m = MessageMemoryData()
    #real unpack if changed
    m.frame = frame
    m.unPack()
    return m

'''
Input messages
'''

class MessageIn(Message):
  def __init__(self):
    Message.__init__(self)
    # GUI
    self.number = 0
  @staticmethod
  def ethAddr (a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
    return b
  def format(self):
    l = "%04d B" % (len(self.frame.payload))
    # new length addrSource addrDest type
    return "%04d %d %s %s %s" % (self.number, self.core, l, MessageIn.ethAddr(self.frame.macSource), MessageIn.ethAddr(self.frame.macDest))
  def formatFull(self):
    l = "%04d B" % (len(self.frame.payload))
    # new length addrSource addrDest type
    return "number : %04d\ncore : %d\nlength : %s\nsrc address : %s\ndest address : %s" % (self.number, self.core, l, MessageIn.ethAddr(self.frame.macSource), MessageIn.ethAddr(self.frame.macDest))

class MessageVMExit(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.VMExit 
    self.exitReason = 0xff
  def format(self):
    return "%s VMExit" % (MessageIn.format(self))
  def unPack(self):
    MessageIn.unPack(self)
    t = unpack('I', self.frame.payload[2:6])
    self.exitReason = t[0]
  def pack(self):
    return MessageIn.pack(self) + pack('I', self.exitReason)
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nexit reason : 0x%x (%d)" % (self.exitReason, self.exitReason & 0xffff)

FILTER=''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
class MessageMemoryData(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.MemoryData
    self.address = 0
    self.length = 0
  def format(self):
    return "%s MemoryData" % (MessageIn.format(self))
  def unPack(self):
    MessageIn.unPack(self)
    t = unpack('qq', self.frame.payload[2:18])
    self.address = t[0]
    self.length = t[1]
    self.data = self.frame.payload[18:18 + self.length] 
  def pack(self):
    return MessageIn.pack(self) + pack('qq', self.address, self.length)
  def formatFull(self):
    return MessageIn.formatFull(self) + "\naddress : 0x%x\nlength : 0x%x\n%s" % (self.address, self.length, self.dump(16, self.address))
  def dump(self, length, n):
    src = self.data
    result=''
    while src:
     s,src = src[:length], src[length:]
     hexa = ' '.join(["%02X" % ord(x) for x in s])
     s = s.translate(FILTER)
     result += "%016X   %-*s   %s\n" % (n, length * 3, hexa, s)
     n += length
    return result

'''
Output messages
'''

class MessageOut(Message):
  def __init__(self):
    Message.__init__(self)

class MessageExecContinue(MessageOut):
  def __init__(self):
    MessageOut.__init__(self)
    self.messageType = Message.ExecContinue

class MessageExecStep(MessageOut):
  def __init__(self):
    MessageOut.__init__(self)
    self.messageType = Message.ExecStep

class MessageMemoryRead(MessageOut):
  def __init__(self, address, length):
    MessageOut.__init__(self)
    self.messageType = Message.MemoryRead
    self.address = address
    self.length = length
  def unPack(self):
    MessageOut.unPack(self)
    t = unpack('qq', self.frame.payload[2:18])
    self.address = t[0]
    self.length = t[0]
  def pack(self):
    return MessageOut.pack(self) + pack('qq', self.address, self.length)
