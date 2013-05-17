from struct import *

class CoreRegs(object):
  def __init__(self):
    # GPRs
    self.rax = None
    self.rbx = None
    self.rcx = None
    self.rdx = None
    self.r8 = None
    self.r9 = None
    self.r10 = None
    self.r11 = None
    self.r12 = None
    self.r13 = None
    self.r14 = None
    self.r15 = None
    # Segment
    self.cs = None
    self.ds = None
    self.ss = None
    self.es = None
    self.fs = None
    self.gs = None
    # Pointer
    self.rbp = None
    self.rsp = None
    # Index
    self.rsi = None
    self.rdi = None
    # Instruction pointer
    self.rip = None
    # Control registers
    self.cr0 = None
    self.cr1 = None
    self.cr2 = None
    self.cr3 = None
    self.cr4 = None
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
      cr3 %016x cr3 %016x
      cr4 %016x
    """ % (
        self.rip, self.rax, self.rbx, self.rcx, self.rdx, self.r8, self.r9,
        self.r10, self.r11, self.r12, self.r13, self.r14, self.r15, self.cs,
        self.ds, self.ss, self.es, self.fs, self.gs, self.rbp, self.rsp,
        self.rsi, self.rdi, self.cr0, self.cr1, self.cr2, self.cr3, self.cr4,
      )

class Core(object):
  def __init__(self):
    self.regs = CoreRegs()
  def unPack(self, data):
    self.regs.unPack(data)
  def format(self):
    return self.regs.format()
