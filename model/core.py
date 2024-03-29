from struct import *

class CoreRegs(object):
  def __init__(self):
    # GPRs
    self.rax = 0
    self.rbx = 0
    self.rcx = 0
    self.rdx = 0
    self.r8 = 0
    self.r9 = 0
    self.r10 = 0
    self.r11 = 0
    self.r12 = 0
    self.r13 = 0
    self.r14 = 0
    self.r15 = 0
    # Segment
    self.cs = 0
    self.ds = 0
    self.ss = 0
    self.es = 0
    self.fs = 0
    self.gs = 0
    # Pointer
    self.rbp = 0
    self.rsp = 0
    # Index
    self.rsi = 0
    self.rdi = 0
    # Instruction pointer
    self.rip = 0
    # Control registers
    self.cr0 = 0
    self.cr1 = 0
    self.cr2 = 0
    self.cr3 = 0
    self.cr4 = 0
    # flags
    self.rflags = 0
    # msrs
    self.ia32_efer = 0
  def unPack(self, data):
    t = unpack('QQQQQQQQQQQQ', data[0:96]) # 12 * 8
    self.rax = t[0]
    self.rbx = t[1]
    self.rcx = t[2]
    self.rdx = t[3]
    self.r8 = t[4]
    self.r9 = t[5]
    self.r10 = t[6]
    self.r11 = t[7]
    self.r12 = t[8]
    self.r13 = t[9]
    self.r14 = t[10]
    self.r15 = t[11]
    t = unpack('HHHHHH', data[96:108]) # 96 + 6 * 2
    self.cs = t[0]
    self.ds = t[1]
    self.ss = t[2]
    self.es = t[3]
    self.fs = t[4]
    self.gs = t[5]
    t = unpack('QQ', data[108:124]) # 108 + 8 * 2
    self.rbp = t[0]
    self.rsp = t[1]
    t = unpack('QQ', data[124:140]) # 124 + 8 * 2
    self.rsi = t[0]
    self.rdi = t[1]
    t = unpack('Q', data[140:148]) # 140 + 8
    self.rip = t[0]
    t = unpack('QQQQQ', data[148:188]) # 148 + 5 * 8
    self.cr0 = t[0]
    self.cr1 = t[1]
    self.cr2 = t[2]
    self.cr3 = t[3]
    self.cr4 = t[4]
    t = unpack('Q', data[188:196]) # 188 + 8
    self.rflags = t[0]
    t = unpack('Q', data[196:204]) # 188 + 8
    self.ia32_efer = t[0]
  def format(self):
    return """
Instruction Pointer
      rip %016x
GPRs  rax %016x rbx %016x
      rcx %016x rdx %016x
      r8  %016x r9  %016x
      r10 %016x r11 %016x
      r12 %016x r13 %016x
      r14 %016x r15 %016x
Segment 
      cs %04x ds %04x
      ss %04x es %04x
      fs %04x gs %04x
Pointer
      rbp %016x rsp %016x
Index
      rsi %016x rdi %016x
Control Registers
      cr0 %016x cr1 %016x
      cr2 %016x cr3 %016x
      cr4 %016x
Flags
      rflags %016x
Msrs
      ia32_efer %016x
    """ % (
        self.rip, self.rax, self.rbx, self.rcx, self.rdx, self.r8, self.r9,
        self.r10, self.r11, self.r12, self.r13, self.r14, self.r15, self.cs,
        self.ds, self.ss, self.es, self.fs, self.gs, self.rbp, self.rsp,
        self.rsi, self.rdi, self.cr0, self.cr1, self.cr2, self.cr3, self.cr4,
        self.rflags, self.ia32_efer
      )

class CoreMode(object):
  (
    REAL,
    PROTECTED,
    IA32E,
    V8086
  ) = range(4)
  class CoreModeError(Exception):
    def __init__(self):
      pass
    def __str__(self):
      return "Core mode error"

class Paging(object):
  (
    DISABLED,
    P32BIT,
    PAE,
    IA32E,
  ) = range(4)
  class PagingError(Exception):
    def __init__(self):
      pass
    def __str__(self):
      return "Paging error"

class Core(object):
  def __init__(self):
    self.regs = CoreRegs()
  def unPack(self, data):
    self.regs.unPack(data)
  def format(self):
    return self.regs.format()
  def getMode(self):
    # Virtual 8086
    if (self.regs.rflags & (1 << 17)):
      return CoreMode.V8086
    # Real
    if not self.regs.cr0 & (1 << 0):
      return CoreMode.REAL
    # Protected mode
    elif self.regs.cr0 & (1 << 0) and not self.regs.ia32_efer & (1 << 10):
      return CoreMode.PROTECTED
    # Long Mode
    elif self.regs.cr0 & (1 << 0) and self.regs.ia32_efer & (1 << 10):
      return CoreMode.IA32E
    raise CoreMode.CoreModeError()
  def getPaging(self):
    if not (self.regs.cr0 & (1 << 0) and self.regs.cr0 & (1 << 31)):
      return Paging.DISABLED
    # 32-Bit Paging
    elif not self.regs.cr4 & (1 << 5) and not self.regs.ia32_efer & (1 << 10):
      return Paging.P32BIT
    # PAE Paging
    elif self.regs.cr4 & (1 << 5) and not self.regs.ia32_efer & (1 << 10):
      return Paging.PAE
    # IA-32e Paging
    elif self.regs.cr4 & (1 << 5) and self.regs.ia32_efer & (1 << 10):
      return Paging.IA32E
    raise Paging.PagingError()

