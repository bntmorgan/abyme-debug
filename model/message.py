from struct import *

import socket, sys, math
from model.core import Core

'''
Message
'''

class BadMessage(BaseException):
  def __str__(self):
    return "Bad message usage"

class Message(object):
  # Message Types
  (
      Message,
      VMExit,
      ExecContinue,
      ExecStep,
      MemoryRead,
      MemoryData,
      MemoryWrite,
      MemoryWriteCommit,
      CoreRegsRead,
      CoreRegsData,
      UnhandledVMExit,
      VMCSRead,
      VMCSData,
  ) = range(13)
  def __init__(self):
    self.messageType = Message.Message
    self.coreNumber = 0
  def unPack(self):
    t = unpack('BB', self.frame.payload[0:2])
    self.messageType = t[0]
    self.coreNumber = t[1]
  def pack(self):
    return pack('BB', self.messageType, self.coreNumber)
  @staticmethod
  def ethAddr (a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
    return b
  def format(self):
    l = "%04d B" % (len(self.frame.payload))
    # new length addrSource addrDest type
    return "%04d %d %s %s %s" % (self.number, self.coreNumber, l, Message.ethAddr(self.frame.macSource), Message.ethAddr(self.frame.macDest))
  def formatFull(self):
    l = "%04d B" % (len(self.frame.payload))
    # new length addrSource addrDest type
    return "number : %04d\ncore : %d\nlength : %s\nsrc address : %s\ndest address : %s" % (self.number, self.coreNumber, l, MessageIn.ethAddr(self.frame.macSource), MessageIn.ethAddr(self.frame.macDest))
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
    elif m.messageType == Message.MemoryWrite:
      m = MessageMemoryWrite()
    elif m.messageType == Message.MemoryWriteCommit:
      m = MessageMemoryWriteCommit()
    elif m.messageType == Message.CoreRegsRead:
      m = MessageCoreRegsRead()
    elif m.messageType == Message.CoreRegsData:
      m = MessageCoreRegsData()
    elif m.messageType == Message.UnhandledVMExit:
      m = MessageUnhandledVMExit()
    elif m.messageType == Message.VMCSRead:
      m = MessageVMCSRead()
    elif m.messageType == Message.VMCSData:
      m = MessageVMCSData()
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

class MessageVMExit(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.VMExit 
    self.exitReason = 0xff
  def format(self):
    return "%s VMExit" % (MessageIn.format(self))
  def unPack(self):
    # unpack exit reason
    MessageIn.unPack(self)
    t = unpack('I', self.frame.payload[2:6])
    self.exitReason = t[0]
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nexit reason : 0x%x (%d)" % (self.exitReason, self.exitReason & 0xffff)

class MessageCoreRegsData(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.CoreRegsData
    self.core = Core()
  def format(self):
    return "%s CoreRegsData" % (MessageIn.format(self))
  def unPack(self):
    # unpack core data
    self.core.unPack(self.frame.payload[2:])
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nCore regs :\n" + self.core.format()

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
    t = unpack('QQ', self.frame.payload[2:18])
    self.address = t[0]
    self.length = t[1]
    self.data = self.frame.payload[18:18 + self.length] 
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

class MessageMemoryWriteCommit(MessageIn):
  def __init__(self, ok = 0):
    MessageIn.__init__(self)
    self.messageType = Message.MemoryWriteCommit
    self.ok = ok
  def unPack(self):
    MessageIn.unPack(self)
    t = unpack('B', self.frame.payload[2])
    self.ok = t[0]
  def format(self):
    return "%s WriteCommit" % (MessageIn.format(self))
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nok : %d" % (self.ok)

class MessageUnhandledVMExit(MessageVMExit):
  def __init__(self):
    MessageVMExit.__init__(self)
    self.messageType = Message.UnhandledVMExit
  def format(self):
    return "%s Unhandled VMExit" % (MessageIn.format(self))

class MessageVMCSData(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.MemoryVMCSData
  def unPack(self):
    MessageIn.unPack(self)
  def format(self):
    return "%s VMCSData" % (MessageIn.format(self))
  def formatFull(self):
    return MessageIn.formatFull(self)

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
  def format(self):
    return "%s ExecContinue" % (MessageOut.format(self))

class MessageExecStep(MessageOut):
  def __init__(self):
    MessageOut.__init__(self)
    self.messageType = Message.ExecStep
  def format(self):
    return "%s ExecStep" % (MessageOut.format(self))

class MessageMemoryRead(MessageOut):
  def __init__(self, address = 0, length = 0):
    MessageOut.__init__(self)
    self.messageType = Message.MemoryRead
    self.address = address
    self.length = length
  def pack(self):
    return MessageOut.pack(self) + pack('QQ', self.address, self.length)
  def format(self):
    return "%s MemoryRead" % (MessageOut.format(self))

class MessageMemoryWrite(MessageOut):
  def __init__(self, address = 0, data = ""):
    MessageOut.__init__(self)
    self.messageType = Message.MemoryWrite
    self.address = address
    self.length = len(data)
    self.data = data
  def pack(self):
    return MessageOut.pack(self) + pack('QQ', self.address, self.length) + self.data
  def format(self):
    return "%s MemoryWrite" % (MessageOut.format(self))

class MessageCoreRegsRead(MessageOut):
  def __init__(self):
    MessageOut.__init__(self)
    self.messageType = Message.CoreRegsRead
  def format(self):
    return "%s CoreRegsRead" % (MessageOut.format(self))

class MessageVMCSRead(MessageOut):
  def __init__(self):
    MessageOut.__init__(self, fields = [], vmcs = None)
    self.messageType = Message.MemoryVMCSData
    self.fields = fields
    self.vmcs = vmcs
    if self.vmcs == None:
      raise BadMessage()
  def pack(self):
    s = MessageOut.pack(self)
    for f in self.fields:
      t = pack('B', self.vmcs.fields[f].length)
      s = s + t
      t = pack('Q', self.vmcs.fields[f].encoding)
      s = s + t
    # Mark the end of message
    t = pack('B', 0)
    s = s + t
    return s
  def format(self):
    return "%s VMCSRead" % (MessageOut.format(self))
  def formatFull(self):
    return MessageOut.formatFull(self)
