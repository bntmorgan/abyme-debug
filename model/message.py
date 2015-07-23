from struct import *

import socket, sys, math
from model.core import Core
from model.vmcs import Encoding
from model.vmm import VMM, ExitReason

'''
Message
'''

class BadMessage(BaseException):
  def __str__(self):
    return "Bad message usage"

class BadVMCSFieldSize(BaseException):
  def __str__(self):
    return "Bad message usage"

class ListItem(object):
  def format(self):
    return "%04d %d " % (self.number, self.vmid)
  def formatFull(self):
    return "number : %04d\ncore : %d\n" % (self.number, self.vmid)

class Message(ListItem):
  # Message Types
  (
      Message,
      VMExit,
      ExecContinue,
      Info,
      MemoryRead,
      MemoryData,
      MemoryWrite,
      Commit, #ACK
      CoreRegsRead,
      CoreRegsData,
      UnhandledVMExit,
      VMCSRead,
      VMCSData,
      VMMPanic,
      VMCSWrite,
      UserDefined,
      SendDebug,
  ) = range(17)
  def __init__(self):
    self.messageType = Message.Message
    # GUI
    self.number = 0
    self.vmid = 0

class Info(Message):
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
  def unPack(self, frame, raw):
    self.frame = frame
    self.raw = raw
    t = unpack('BB', self.raw[0:2])
    self.messageType = t[0]
    self.vmid = t[1]
  def pack(self):
    return pack('BB', self.messageType, self.vmid)
  @staticmethod
  def ethAddr (a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
    return b
  def format(self):
    l = "%04d B" % (len(self.raw))
    # new length addrSource addrDest type
    return Message.format(self) + "%s %s %s" % (l, MessageNetwork.ethAddr(self.frame.macSource), MessageNetwork.ethAddr(self.frame.macDest))
  def formatFull(self):
    l = "%04d B" % (len(self.raw))
    # new length addrSource addrDest type
    return Message.formatFull(self) + "length : %s\nsrc address : %s\ndest address : %s" % (l, MessageNetwork.ethAddr(self.frame.macSource), MessageNetwork.ethAddr(self.frame.macDest))
  @staticmethod
  def createMessage(frame, raw):
    # get the type of the message
    m = MessageIn();
    m.unPack(frame, raw)
    # get the real message
    if m.messageType == Message.VMExit:
      m = MessageVMExit()
    elif m.messageType == Message.ExecContinue:
      m = MessageExecContinue()
    elif m.messageType == Message.Info:
      m = MessageInfo()
    elif m.messageType == Message.MemoryRead:
      m = MessageMemoryRead()
    elif m.messageType == Message.MemoryData:
      m = MessageMemoryData()
    elif m.messageType == Message.MemoryWrite:
      m = MessageMemoryWrite()
    elif m.messageType == Message.Commit:
      m = MessageCommit()
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
    elif m.messageType == Message.UserDefined:
      m = MessageUserDefined()
    elif m.messageType == Message.SendDebug:
      m = MessageSendDebug()
    #real unpack if changed
    m.unPack(frame, raw)
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
    self.core = Core()
  def format(self):
    return "%s VMExit (%s)" % (MessageIn.format(self), ExitReason.e[self.exitReason & 0xffff]['name'])
  def unPack(self, frame, raw):
    # unpack exit reason
    MessageIn.unPack(self, frame, raw)
    t = unpack('I', self.raw[2:6])
    self.exitReason = t[0]
    self.core.unPack(self.raw[6:])
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nexit reason : 0x%x (%d) : %s" % (self.exitReason, self.exitReason & 0xffff, ExitReason.e[self.exitReason & 0xffff]['name'])

class MessageCoreRegsData(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.CoreRegsData
    self.core = Core()
  def format(self):
    return "%s CoreRegsData" % (MessageIn.format(self))
  def unPack(self, frame, raw):
    MessageIn.unPack(self, frame, raw)
    # unpack core data
    self.core.unPack(self.raw[2:])
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nCore regs :\n" + self.core.format()

class MessageInfo(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.Info
    self.length = 0
    self.level = 0
    self.data = None
  def format(self):
    return "%s MessageInfo" % (MessageIn.format(self))
  def unPack(self, frame, raw):
    MessageIn.unPack(self, frame, raw)
    t = unpack('QI', self.raw[2:14])
    self.length = t[0]
    self.level = t[1]
    self.data = self.raw[14:14 + self.length]
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nlength : 0x%x\n%s" % (self.length,
      self.data)
  def getString(self):
    return self.data

FILTER=''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
class MessageMemoryData(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.MemoryData
    self.address = 0
    self.length = 0
    self.data = None
  def format(self):
    return "%s MemoryData" % (MessageIn.format(self))
  def unPack(self, frame, raw):
    MessageIn.unPack(self, frame, raw)
    t = unpack('QQ', self.raw[2:18])
    self.address = t[0]
    self.length = t[1]
    self.data = self.raw[18:18 + self.length]
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

class MessageCommit(MessageIn):
  def __init__(self, ok = 0):
    MessageIn.__init__(self)
    self.messageType = Message.Commit
    self.ok = ok
  def unPack(self, frame, raw):
    MessageIn.unPack(self, frame, raw)
    t = unpack('B', self.raw[2])
    self.ok = t[0]
  def format(self):
    return "%s Commit" % (MessageIn.format(self))
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
  def unPack(self, frame, raw):
    MessageIn.unPack(self, frame, raw)
    # Copy the VMCS Fields
    data = self.raw[2:]
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

panic = {
  0: 'VMM_PANIC_RDMSR',
  1: 'VMM_PANIC_WRMSR',
  2: 'VMM_PANIC_CR_ACCESS',
  3: 'VMM_PANIC_UNKNOWN_CPU_MODE',
  4: 'VMM_PANIC_IO',
  5: 'VMM_PANIC_XSETBV'
};

class MessageVMMPanic(MessageIn):
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.VMMPanic
    self.code = 0
    self.extra = 0
  def unPack(self, frame, raw):
    MessageIn.unPack(self, frame, raw)
    self.code = unpack("Q", self.raw[2:10])[0]
    self.extra = unpack("Q", self.raw[10:18])[0]
  def format(self):
    return "%s Vmm Panic : code %d, extra %d (%s)" % (MessageIn.format(self), self.code, self.extra, panic[self.code])

class MessageUserDefined(MessageIn):
  # Message Types
  (
    LogCR3,
    LogMD5,
  ) = range(2)
  def __init__(self):
    MessageIn.__init__(self)
    self.messageType = Message.UserDefined
    self.userType = None
    self.length = None
    self.data = None
  def format(self):
    return "%s User Defined" % (MessageIn.format(self))
  def unPack(self, frame, raw):
    MessageIn.unPack(self, frame, raw)
    t = unpack('H', self.raw[2:4])
    self.userType = t[0]
    t = unpack('Q', self.raw[4:12])
    self.length = t[0]
    self.data = self.raw[12:12 + self.length]
  def formatFull(self):
    return MessageIn.formatFull(self) + "\nuserType : 0x%x\nlength : 0x%x\n%s" % (self.userType, self.length, self.dump(16, 0))
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

class MessageSendDebug(MessageOut):
  def __init__(self, sendDebug = {}):
    MessageOut.__init__(self)
    self.messageType = Message.SendDebug
    self.sendDebug = sendDebug
    self.r = [0] * ExitReason.number
  def pack(self):
    s = MessageOut.pack(self)
    for k, r in self.sendDebug.iteritems():
      self.r[r.encoding] = r.active
    for i in range(0, ExitReason.number):
      t = pack('B', self.r[i])
      s = s + t
    return s
  def format(self):
    return "%s SendDebug" % (MessageOut.format(self))
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
