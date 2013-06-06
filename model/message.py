from struct import *

import socket, sys, math
from model.core import Core
from model.vmcs import Encoding
from model.vmm import basic_exit_reasons

'''
Message
'''

class BadMessage(BaseException):
  def __str__(self):
    return "Bad message usage"

class BadVMCSFieldSize(BaseException):
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
      VMMPanic,
      VMCSWrite,
      VMCSWriteCommit,
  ) = range(16)
  def __init__(self):
    self.messageType = Message.Message
    # GUI
    self.number = 0
    self.coreNumber = 0
  def format(self):
    return "%04d %d " % (self.number, self.coreNumber)
  def formatFull(self):
    return "number : %04d\ncore : %d\n" % (self.number, self.coreNumber)

class MessageInfo(Message):
  def __init__(self, label, message):
    Message.__init__(self)
    self.label = label
    self.message = message
  def format(self):
    return Message.format(self) + '-' * 42 + " Info : " + self.label
  def formatFull(self):
    return Message.formatFull(self) + self.message

class MessageNetwork(Message):
  def __init__(self):
    Message.__init__(self)
    self.frame = None
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
    return Message.format(self) + "%s %s %s" % (l, MessageNetwork.ethAddr(self.frame.macSource), MessageNetwork.ethAddr(self.frame.macDest))
  def formatFull(self):
    l = "%04d B" % (len(self.frame.payload))
    # new length addrSource addrDest type
    return Message.formatFull(self) + "length : %s\nsrc address : %s\ndest address : %s" % (l, MessageNetwork.ethAddr(self.frame.macSource), MessageNetwork.ethAddr(self.frame.macDest))
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
    elif m.messageType == Message.VMMPanic:
      m = MessageVMMPanic()
    elif m.messageType == Message.VMCSWrite:
      m = MessageVMCSWrite()
    elif m.messageType == Message.VMCSWriteCommit:
      m = MessageVMCSWriteCommit()
    #real unpack if changed
    m.frame = frame
    m.unPack()
    return m


'''
Input messages
'''

class MessageIn(MessageNetwork):
  def __init__(self):
    MessageNetwork.__init__(self)

class MessageVMExit(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.VMExit 
    self.exitReason = 0xff
  def format(self):
    return "%s VMExit (%s)" % (MessageIn.format(self), basic_exit_reasons[self.exitReason & 0xffff])
  def unPack(self):
    # unpack exit reason
    MessageIn.unPack(self)
    t = unpack('I', self.frame.payload[2:6])
    self.exitReason = t[0]
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nexit reason : 0x%x (%d) : %s" % (self.exitReason, self.exitReason & 0xffff, basic_exit_reasons[self.exitReason & 0xffff])

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
    self.messageType = Message.VMCSData
    self.vmcs = None
    # Received fields for display purpose
    self.fields = {}
  def unPack(self):
    MessageIn.unPack(self)
    # Copy the VMCS Fields
    data = self.frame.payload[2:]
    s = unpack("B", data[0])[0]
    while s > 0:
      e = unpack("Q", data[1:9])[0]
      v = 0
      if s == 2:
        v = unpack("H", data[9:11])[0]
      elif s == 4:
        v = unpack("I", data[9:13])[0]
      elif s == 8:
        v = unpack("Q", data[9:17])[0]
      else:
        raise BadVMCSFieldSize()
      data = data[1 + 8 + s:]
      s = unpack("B", data[0])[0]
      f = Encoding.e[e]['c'](e)
      f.value = v
      self.fields[f.name] = f
  def format(self):
    return "%s VMCSData" % (MessageIn.format(self))
  def formatFull(self):
    s = ''
    for k, f in self.fields.iteritems():
      s = s + f.format() + "\n"
    return MessageIn.formatFull(self) + '\n' + s

class MessageVMMPanic(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.VMMPanic
    self.code = 0
    self.extra = 0
  def unPack(self):
    MessageIn.unPack(self)
    self.code = unpack("Q", self.frame.payload[2:10])[0]
    self.extra = unpack("Q", self.frame.payload[10:18])[0]
  def format(self):
    return "%s Vmm Panic : code %d, extra %d" % (MessageIn.format(self), self.code, self.extra)

class MessageVMCSWriteCommit(MessageIn):
  def __init__(self, ok = 0):
    MessageIn.__init__(self)
    self.messageType = Message.VMCSWriteCommit
    self.ok = ok
  def unPack(self):
    MessageIn.unPack(self)
    t = unpack('B', self.frame.payload[2])
    self.ok = t[0]
  def format(self):
    return "%s VMCSWriteCommit" % (MessageIn.format(self))
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nok : %d" % (self.ok)

'''
Output messages
'''

class MessageOut(MessageNetwork):
  def __init__(self):
    MessageNetwork.__init__(self)

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
  def __init__(self, fields = []):
    MessageOut.__init__(self)
    self.messageType = Message.VMCSRead
    self.fields = fields
  def pack(self):
    s = MessageOut.pack(self)
    for k, f in self.fields.iteritems():
      t = pack('B', f.length)
      s = s + t
      t = pack('Q', f.encoding)
      s = s + t
    # Mark the end of message
    t = pack('B', 0)
    s = s + t
    return s
  def format(self):
    return "%s VMCSRead" % (MessageOut.format(self))
  def formatFull(self):
    return MessageOut.formatFull(self)

class MessageVMCSWrite(MessageOut):
  def __init__(self, fields = []):
    MessageOut.__init__(self)
    self.messageType = Message.VMCSWrite
    self.fields = fields
  def pack(self):
    s = MessageOut.pack(self)
    for k, f in self.fields.iteritems():
      s = s + f.pack()
    # Mark the end of message
    t = pack('B', 0)
    s = s + t
    return s
  def format(self):
    return "%s VMCSWrite" % (MessageOut.format(self))
  def formatFull(self):
    return MessageOut.formatFull(self)
