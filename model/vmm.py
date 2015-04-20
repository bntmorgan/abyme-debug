class ExitReason(object):
  number = 65
  e = {
    0: {'name': 'EXCEPTION_OR_NMI'},
    1: {'name': 'EXTERNAL_INTERRUPT'},
    2: {'name': 'TRIPLE_FAULT'},
    3: {'name': 'INIT_SIGNAL'},
    4: {'name': 'SIPI'},
    5: {'name': 'IO_SMI'},
    6: {'name': 'OTHER_SMI'},
    7: {'name': 'INTR_WINDOW'},
    8: {'name': 'NMI_WINDOW'},
    9: {'name': 'TASK_SWITCH'},
    10: {'name': 'CPUID'},
    11: {'name': 'GETSEC'},
    12: {'name': 'HLT'},
    13: {'name': 'INVD'},
    14: {'name': 'INVLPG'},
    15: {'name': 'RDPMC'},
    16: {'name': 'RDTSC'},
    17: {'name': 'RSM'},
    18: {'name': 'VMCALL'},
    19: {'name': 'VMCLEAR'},
    20: {'name': 'VMLAUNCH'},
    21: {'name': 'VMPTRLD'},
    22: {'name': 'VMPTRST'},
    23: {'name': 'VMREAD'},
    24: {'name': 'VMRESUME'},
    25: {'name': 'VMWRITE'},
    26: {'name': 'VMXOFF'},
    27: {'name': 'VMXON'},
    28: {'name': 'CR_ACCESS'},
    29: {'name': 'MOV_DR'},
    30: {'name': 'IO_INSTRUCTION'},
    31: {'name': 'RDMSR'},
    32: {'name': 'WRMSR'},
    33: {'name': 'INVALID_GUEST_STATE'},
    34: {'name': 'MSR_LOADING_FAILED'},
    36: {'name': 'MWAIT'},
    37: {'name': 'MONITOR_TRAP_FLAG'},
    39: {'name': 'MONITOR'},
    40: {'name': 'PAUSE'},
    41: {'name': 'MCE_DURING_VM_ENTRY'},
    43: {'name': 'TPR_BELOW_THRESHOLD'},
    44: {'name': 'APIC_ACCESS'},
    45: {'name': 'VIRTUALIZED_EOI'},
    46: {'name': 'ACCESS_GDTR_OR_IDTR'},
    47: {'name': 'ACCESS_LDTR_OR_TR'},
    48: {'name': 'EPT_VIOLATION'},
    49: {'name': 'EPT_MISCONFIG'},
    50: {'name': 'INVEPT'},
    51: {'name': 'RDTSCP'},
    52: {'name': 'VMX_PREEMPTION_TIMER_EXPIRED'},
    53: {'name': 'INVVPID'},
    54: {'name': 'WBINVD'},
    55: {'name': 'XSETBV'},
    56: {'name': 'APIC_WRITE'},
    57: {'name': 'RDRAND'},
    58: {'name': 'INVPCID'},
    59: {'name': 'VMFUNC'},
    61: {'name': 'RDSEED'},
    63: {'name': 'XSAVES'},
    64: {'name': 'XRSTORS'},
  }
  def __init__(self, encoding, active):
    self.encoding = encoding
    self.name = ExitReason.e[encoding]['name']
    self.active = active
  def toggle(self):
    self.active = 1 if self.active == 0 else 0

class VMM(object):
  def __init__(self):
    self.sendDebug = {}
  def setAll(self):
    for k, v in self.sendDebug.iteritems():
      v.active = 1
  def setNone(self):
    for k, v in self.sendDebug.iteritems():
      v.active = 0
    # We preserve VMX preemption timer
    self.sendDebug['VMX_PREEMPTION_TIMER_EXPIRED'].active = 1
  def setDefault(self):
    self.setAll()
    self.sendDebug['CPUID'].active = 0
    self.sendDebug['IO_INSTRUCTION'].active = 0
    self.sendDebug['WRMSR'].active = 0
    self.sendDebug['RDMSR'].active = 0
    self.sendDebug['XSETBV'].active = 0
    self.sendDebug['CR_ACCESS'].active = 0
    self.sendDebug['INVVPID'].active = 0
    self.sendDebug['VMRESUME'].active = 0
    self.sendDebug['VMREAD'].active = 0
    self.sendDebug['VMWRITE'].active = 0
  @staticmethod
  def createVMM():
    vmm = VMM()
    for k, v in ExitReason.e.iteritems():
      vmm.sendDebug[v['name']] = ExitReason(k, 1)
    vmm.setDefault()
    return vmm
