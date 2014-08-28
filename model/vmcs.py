from struct import *

class VMCSField(object):
  def __init__(self):
    self.length = 0
    self.encoding = 0
    self.name = ''
    self.value = 0
  def format(self):
    return self.name + '(' + '0x%x' % (self.encoding) + ') : ' + '0x%x' % (self.value)

class VMCSField16(VMCSField):
  def __init__(self, encoding):
    VMCSField.__init__(self)
    self.length = 2
    self.encoding = encoding
    self.name = Encoding.e[self.encoding]['name']
  def pack(self):
    return pack('B', self.length) + pack('Q', self.encoding) + pack('H', self.value)

class VMCSField32(VMCSField):
  def __init__(self, encoding):
    VMCSField.__init__(self)
    self.length = 4
    self.encoding = encoding
    self.name = Encoding.e[self.encoding]['name']
  def pack(self):
    return pack('B', self.length) + pack('Q', self.encoding) + pack('I', self.value)

class VMCSField64(VMCSField):
  def __init__(self, encoding):
    VMCSField.__init__(self)
    self.length = 8
    self.encoding = encoding
    self.name = Encoding.e[self.encoding]['name']
  def pack(self):
    return pack('B', self.length) + pack('Q', self.encoding) + pack('Q', self.value)

class VMCSFieldNW(VMCSField):
  def __init__(self, encoding):
    VMCSField.__init__(self)
    self.length = 8
    self.encoding = encoding
    self.name = Encoding.e[self.encoding]['name']
  def pack(self):
    return pack('B', self.length) + pack('Q', self.encoding) + pack('Q', self.value)

class VMCS(object):
  def __init__(self):
    # XXX
    self.core = None
    self.fields = {}
  @staticmethod
  def createVMCS(core = None):
    vmcs = VMCS()
    f = None
    for k, v in Encoding.e.iteritems():
      f = v['c'](k);
      vmcs.fields[f.name] = f
    return vmcs

class Encoding(object):
  e = {
    # 16-BIT FIELDS
    # 16-Bit Control Fields
    0x00000000: {'name': 'VIRTUAL_PROCESSOR_ID', 'c': VMCSField16},
    0x00000002: {'name': 'POSTED_INT_NOTIF_VECTOR', 'c': VMCSField16},
    0x00000004: {'name': 'EPTP_INDEX', 'c': VMCSField16},
    # 16-Bit Guest-State Fields
    0x00000800: {'name': 'GUEST_ES_SELECTOR', 'c': VMCSField16},
    0x00000802: {'name': 'GUEST_CS_SELECTOR', 'c': VMCSField16},
    0x00000804: {'name': 'GUEST_SS_SELECTOR', 'c': VMCSField16},
    0x00000806: {'name': 'GUEST_DS_SELECTOR', 'c': VMCSField16},
    0x00000808: {'name': 'GUEST_FS_SELECTOR', 'c': VMCSField16},
    0x0000080a: {'name': 'GUEST_GS_SELECTOR', 'c': VMCSField16},
    0x0000080c: {'name': 'GUEST_LDTR_SELECTOR', 'c': VMCSField16},
    0x0000080e: {'name': 'GUEST_TR_SELECTOR', 'c': VMCSField16},
    0x00000810: {'name': 'GUEST_INTERRUPT_STATUS', 'c': VMCSField16},
    # 16-Bit Host-State Fields
    0x00000c00: {'name': 'HOST_ES_SELECTOR', 'c': VMCSField16},
    0x00000c02: {'name': 'HOST_CS_SELECTOR', 'c': VMCSField16},
    0x00000c04: {'name': 'HOST_SS_SELECTOR', 'c': VMCSField16},
    0x00000c06: {'name': 'HOST_DS_SELECTOR', 'c': VMCSField16},
    0x00000c08: {'name': 'HOST_FS_SELECTOR', 'c': VMCSField16},
    0x00000c0a: {'name': 'HOST_GS_SELECTOR', 'c': VMCSField16},
    0x00000c0c: {'name': 'HOST_TR_SELECTOR', 'c': VMCSField16},
    # 64-BIT FIELDS
    # 64-Bit Control Fields
    0x00002000: {'name': 'IO_BITMAP_A', 'c': VMCSField64},
    0x00002001: {'name': 'IO_BITMAP_A_HIGH', 'c': VMCSField64},
    0x00002002: {'name': 'IO_BITMAP_B', 'c': VMCSField64},
    0x00002003: {'name': 'IO_BITMAP_B_HIGH', 'c': VMCSField64},
    0x00002004: {'name': 'MSR_BITMAP', 'c': VMCSField64},
    0x00002005: {'name': 'MSR_BITMAP_HIGH', 'c': VMCSField64},
    0x00002006: {'name': 'VM_EXIT_MSR_STORE_ADDR', 'c': VMCSField64},
    0x00002007: {'name': 'VM_EXIT_MSR_STORE_ADDR_HIGH', 'c': VMCSField64},
    0x00002008: {'name': 'VM_EXIT_MSR_LOAD_ADDR', 'c': VMCSField64},
    0x00002009: {'name': 'VM_EXIT_MSR_LOAD_ADDR_HIGH', 'c': VMCSField64},
    0x0000200a: {'name': 'VM_ENTRY_MSR_LOAD_ADDR', 'c': VMCSField64},
    0x0000200b: {'name': 'VM_ENTRY_MSR_LOAD_ADDR_HIGH', 'c': VMCSField64},
    0x0000200c: {'name': 'EXECUTIVE_VMCS_POINTER', 'c': VMCSField64},
    0x0000200d: {'name': 'EXECUTIVE_VMCS_POINTER_HIGH', 'c': VMCSField64},
    0x00002010: {'name': 'TSC_OFFSET', 'c': VMCSField64},
    0x00002011: {'name': 'TSC_OFFSET_HIGH', 'c': VMCSField64},
    0x00002012: {'name': 'VIRTUAL_APIC_PAGE_ADDR', 'c': VMCSField64},
    0x00002013: {'name': 'VIRTUAL_APIC_PAGE_ADDR_HIGH', 'c': VMCSField64},
    0x00002014: {'name': 'APIC_ACCESS_ADDR', 'c': VMCSField64},
    0x00002015: {'name': 'APIC_ACCESS_ADDR_HIGH', 'c': VMCSField64},
    0x00002016: {'name': 'POSTED_INTR_DESC_ADDR', 'c': VMCSField64},
    0x00002017: {'name': 'POSTED_INTR_DESC_ADDR_HIGH', 'c': VMCSField64},
    0x00002018: {'name': 'VM_FUNCTION_CONTROLS', 'c': VMCSField64},
    0x00002019: {'name': 'VM_FUNCTION_CONTROLS_HIGH', 'c': VMCSField64},
    0x0000201a: {'name': 'EPT_POINTER', 'c': VMCSField64},
    0x0000201b: {'name': 'EPT_POINTER_HIGH', 'c': VMCSField64},
    0x0000201c: {'name': 'EOI_EXIT_BITMAP_0', 'c': VMCSField64},
    0x0000201d: {'name': 'EOI_EXIT_BITMAP_0_HIGH', 'c': VMCSField64},
    0x0000201e: {'name': 'EOI_EXIT_BITMAP_1', 'c': VMCSField64},
    0x0000201f: {'name': 'EOI_EXIT_BITMAP_1_HIGH', 'c': VMCSField64},
    0x00002020: {'name': 'EOI_EXIT_BITMAP_2', 'c': VMCSField64},
    0x00002021: {'name': 'EOI_EXIT_BITMAP_2_HIGH', 'c': VMCSField64},
    0x00002022: {'name': 'EOI_EXIT_BITMAP_3', 'c': VMCSField64},
    0x00002023: {'name': 'EOI_EXIT_BITMAP_3_HIGH', 'c': VMCSField64},
    0x00002024: {'name': 'EPTP_LIST_ADDR', 'c': VMCSField64},
    0x00002025: {'name': 'EPTP_LIST_ADDR_HIGH', 'c': VMCSField64},
    0x00002026: {'name': 'VMREAD_BITMAP_ADDR', 'c': VMCSField64},
    0x00002027: {'name': 'VMREAD_BITMAP_ADDR_HIGH', 'c': VMCSField64},
    0x00002028: {'name': 'VMWRITE_BITMAP_ADDR', 'c': VMCSField64},
    0x00002029: {'name': 'VMWRITE_BITMAP_ADDR_HIGH', 'c': VMCSField64},
    0x0000202a: {'name': 'VIRT_EXCEP_INFO_ADDR', 'c': VMCSField64},
    0x0000202b: {'name': 'VIRT_EXCEP_INFO_ADDR_HIGH', 'c': VMCSField64},
    0x0000202c: {'name': 'XSS_EXITING_BITMAP', 'c': VMCSField64},
    0x0000202d: {'name': 'XSS_EXITING_BITMAP_HIGH', 'c': VMCSField64},
    # 64-Bit Read-Only Data Field
    0x00002400: {'name': 'GUEST_PHYSICAL_ADDRESS', 'c': VMCSField64},
    0x00002401: {'name': 'GUEST_PHYSICAL_ADDRESS_HIGH', 'c': VMCSField64},
    # 64-Bit Guest-State Fields
    0x00002800: {'name': 'VMCS_LINK_POINTER', 'c': VMCSField64},
    0x00002801: {'name': 'VMCS_LINK_POINTER_HIGH', 'c': VMCSField64},
    0x00002802: {'name': 'GUEST_IA32_DEBUGCTL', 'c': VMCSField64},
    0x00002803: {'name': 'GUEST_IA32_DEBUGCTL_HIGH', 'c': VMCSField64},
    0x00002804: {'name': 'GUEST_IA32_PAT', 'c': VMCSField64},
    0x00002805: {'name': 'GUEST_IA32_PAT_HIGH', 'c': VMCSField64},
    0x00002806: {'name': 'GUEST_IA32_EFER', 'c': VMCSField64},
    0x00002807: {'name': 'GUEST_IA32_EFER_HIGH', 'c': VMCSField64},
    0x00002808: {'name': 'GUEST_IA32_PERF_GLOBAL_CTRL', 'c': VMCSField64},
    0x00002809: {'name': 'GUEST_IA32_PERF_GLOBAL_CTRL_HIGH', 'c': VMCSField64},
    0x0000280a: {'name': 'GUEST_PDPTR0', 'c': VMCSField64},
    0x0000280b: {'name': 'GUEST_PDPTR0_HIGH', 'c': VMCSField64},
    0x0000280c: {'name': 'GUEST_PDPTR1', 'c': VMCSField64},
    0x0000280d: {'name': 'GUEST_PDPTR1_HIGH', 'c': VMCSField64},
    0x0000280e: {'name': 'GUEST_PDPTR2', 'c': VMCSField64},
    0x0000280f: {'name': 'GUEST_PDPTR2_HIGH', 'c': VMCSField64},
    0x00002810: {'name': 'GUEST_PDPTR3', 'c': VMCSField64},
    0x00002811: {'name': 'GUEST_PDPTR3_HIGH', 'c': VMCSField64},
    # 64-Bit Host-State Fields
    0x00002c00: {'name': 'HOST_IA32_PAT', 'c': VMCSField64},
    0x00002c01: {'name': 'HOST_IA32_PAT_HIGH', 'c': VMCSField64},
    0x00002c02: {'name': 'HOST_IA32_EFER', 'c': VMCSField64},
    0x00002c03: {'name': 'HOST_IA32_EFER_HIGH', 'c': VMCSField64},
    0x00002c04: {'name': 'HOST_IA32_PERF_GLOBAL_CTRL', 'c': VMCSField64},
    0x00002c05: {'name': 'HOST_IA32_PERF_GLOBAL_CTRL_HIGH', 'c': VMCSField64},
    # 32-BIT FIELDS
    # 32-Bit Control Fields
    0x00004000: {'name': 'PIN_BASED_VM_EXEC_CONTROL', 'c': VMCSField32},
    0x00004002: {'name': 'CPU_BASED_VM_EXEC_CONTROL', 'c': VMCSField32},
    0x00004004: {'name': 'EXCEPTION_BITMAP', 'c': VMCSField32},
    0x00004006: {'name': 'PAGE_FAULT_ERROR_CODE_MASK', 'c': VMCSField32},
    0x00004008: {'name': 'PAGE_FAULT_ERROR_CODE_MATCH', 'c': VMCSField32},
    0x0000400a: {'name': 'CR3_TARGET_COUNT', 'c': VMCSField32},
    0x0000400c: {'name': 'VM_EXIT_CONTROLS', 'c': VMCSField32},
    0x0000400e: {'name': 'VM_EXIT_MSR_STORE_COUNT', 'c': VMCSField32},
    0x00004010: {'name': 'VM_EXIT_MSR_LOAD_COUNT', 'c': VMCSField32},
    0x00004012: {'name': 'VM_ENTRY_CONTROLS', 'c': VMCSField32},
    0x00004014: {'name': 'VM_ENTRY_MSR_LOAD_COUNT', 'c': VMCSField32},
    0x00004016: {'name': 'VM_ENTRY_INTR_INFO_FIELD', 'c': VMCSField32},
    0x00004018: {'name': 'VM_ENTRY_EXCEPTION_ERROR_CODE', 'c': VMCSField32},
    0x0000401a: {'name': 'VM_ENTRY_INSTRUCTION_LEN', 'c': VMCSField32},
    0x0000401c: {'name': 'TPR_THRESHOLD', 'c': VMCSField32},
    0x0000401e: {'name': 'SECONDARY_VM_EXEC_CONTROL', 'c': VMCSField32},
    0x00004020: {'name': 'PLE_GAP', 'c': VMCSField32},
    0x00004022: {'name': 'PLE_WINDOW', 'c': VMCSField32},
    # 32-Bit Read-Only Data Fields
    0x00004400: {'name': 'VM_INSTRUCTION_ERROR', 'c': VMCSField32},
    0x00004402: {'name': 'VM_EXIT_REASON', 'c': VMCSField32},
    0x00004404: {'name': 'VM_EXIT_INTR_INFO', 'c': VMCSField32},
    0x00004406: {'name': 'VM_EXIT_INTR_ERROR_CODE', 'c': VMCSField32},
    0x00004408: {'name': 'IDT_VECTORING_INFO_FIELD', 'c': VMCSField32},
    0x0000440a: {'name': 'IDT_VECTORING_ERROR_CODE', 'c': VMCSField32},
    0x0000440c: {'name': 'VM_EXIT_INSTRUCTION_LEN', 'c': VMCSField32},
    0x0000440e: {'name': 'VMX_INSTRUCTION_INFO', 'c': VMCSField32},
    # 32-Bit Guest-State Fields
    0x00004800: {'name': 'GUEST_ES_LIMIT', 'c': VMCSField32},
    0x00004802: {'name': 'GUEST_CS_LIMIT', 'c': VMCSField32},
    0x00004804: {'name': 'GUEST_SS_LIMIT', 'c': VMCSField32},
    0x00004806: {'name': 'GUEST_DS_LIMIT', 'c': VMCSField32},
    0x00004808: {'name': 'GUEST_FS_LIMIT', 'c': VMCSField32},
    0x0000480a: {'name': 'GUEST_GS_LIMIT', 'c': VMCSField32},
    0x0000480c: {'name': 'GUEST_LDTR_LIMIT', 'c': VMCSField32},
    0x0000480e: {'name': 'GUEST_TR_LIMIT', 'c': VMCSField32},
    0x00004810: {'name': 'GUEST_GDTR_LIMIT', 'c': VMCSField32},
    0x00004812: {'name': 'GUEST_IDTR_LIMIT', 'c': VMCSField32},
    0x00004814: {'name': 'GUEST_ES_AR_BYTES', 'c': VMCSField32},
    0x00004816: {'name': 'GUEST_CS_AR_BYTES', 'c': VMCSField32},
    0x00004818: {'name': 'GUEST_SS_AR_BYTES', 'c': VMCSField32},
    0x0000481a: {'name': 'GUEST_DS_AR_BYTES', 'c': VMCSField32},
    0x0000481c: {'name': 'GUEST_FS_AR_BYTES', 'c': VMCSField32},
    0x0000481e: {'name': 'GUEST_GS_AR_BYTES', 'c': VMCSField32},
    0x00004820: {'name': 'GUEST_LDTR_AR_BYTES', 'c': VMCSField32},
    0x00004822: {'name': 'GUEST_TR_AR_BYTES', 'c': VMCSField32},
    0x00004824: {'name': 'GUEST_INTERRUPTIBILITY_INFO', 'c': VMCSField32},
    0x00004826: {'name': 'GUEST_ACTIVITY_STATE', 'c': VMCSField32},
    0x00004828: {'name': 'GUEST_SMBASE', 'c': VMCSField32},
    0x0000482a: {'name': 'GUEST_SYSENTER_CS', 'c': VMCSField32},
    0x0000482e: {'name': 'VMX_PREEMPTION_TIMER_VALUE', 'c': VMCSField32},
    # 32-Bit Host-State Field
    0x00004c00: {'name': 'HOST_IA32_SYSENTER_CS', 'c': VMCSField32},
    # NATURAL-WIDTH FIELDS
    # Natural-Width Control Fields
    0x00006000: {'name': 'CR0_GUEST_HOST_MASK', 'c': VMCSFieldNW},
    0x00006002: {'name': 'CR4_GUEST_HOST_MASK', 'c': VMCSFieldNW},
    0x00006004: {'name': 'CR0_READ_SHADOW', 'c': VMCSFieldNW},
    0x00006006: {'name': 'CR4_READ_SHADOW', 'c': VMCSFieldNW},
    0x00006008: {'name': 'CR3_TARGET_VALUE0', 'c': VMCSFieldNW},
    0x0000600a: {'name': 'CR3_TARGET_VALUE1', 'c': VMCSFieldNW},
    0x0000600c: {'name': 'CR3_TARGET_VALUE2', 'c': VMCSFieldNW},
    0x0000600e: {'name': 'CR3_TARGET_VALUE3', 'c': VMCSFieldNW},
    # Natural-Width Read-Only Data Fields
    0x00006400: {'name': 'EXIT_QUALIFICATION', 'c': VMCSFieldNW},
    0x00006402: {'name': 'IO_RCX', 'c': VMCSFieldNW},
    0x00006404: {'name': 'IO_RSI', 'c': VMCSFieldNW},
    0x00006406: {'name': 'IO_RDI', 'c': VMCSFieldNW},
    0x00006408: {'name': 'IO_RIP', 'c': VMCSFieldNW},
    0x0000640a: {'name': 'GUEST_LINEAR_ADDRESS', 'c': VMCSFieldNW},
    # Natural-Width Guest-State Fields
    0x00006800: {'name': 'GUEST_CR0', 'c': VMCSFieldNW},
    0x00006802: {'name': 'GUEST_CR3', 'c': VMCSFieldNW},
    0x00006804: {'name': 'GUEST_CR4', 'c': VMCSFieldNW},
    0x00006806: {'name': 'GUEST_ES_BASE', 'c': VMCSFieldNW},
    0x00006808: {'name': 'GUEST_CS_BASE', 'c': VMCSFieldNW},
    0x0000680a: {'name': 'GUEST_SS_BASE', 'c': VMCSFieldNW},
    0x0000680c: {'name': 'GUEST_DS_BASE', 'c': VMCSFieldNW},
    0x0000680e: {'name': 'GUEST_FS_BASE', 'c': VMCSFieldNW},
    0x00006810: {'name': 'GUEST_GS_BASE', 'c': VMCSFieldNW},
    0x00006812: {'name': 'GUEST_LDTR_BASE', 'c': VMCSFieldNW},
    0x00006814: {'name': 'GUEST_TR_BASE', 'c': VMCSFieldNW},
    0x00006816: {'name': 'GUEST_GDTR_BASE', 'c': VMCSFieldNW},
    0x00006818: {'name': 'GUEST_IDTR_BASE', 'c': VMCSFieldNW},
    0x0000681a: {'name': 'GUEST_DR7', 'c': VMCSFieldNW},
    0x0000681c: {'name': 'GUEST_RSP', 'c': VMCSFieldNW},
    0x0000681e: {'name': 'GUEST_RIP', 'c': VMCSFieldNW},
    0x00006820: {'name': 'GUEST_RFLAGS', 'c': VMCSFieldNW},
    0x00006822: {'name': 'GUEST_PENDING_DBG_EXCEPTIONS', 'c': VMCSFieldNW},
    0x00006824: {'name': 'GUEST_SYSENTER_ESP', 'c': VMCSFieldNW},
    0x00006826: {'name': 'GUEST_SYSENTER_EIP', 'c': VMCSFieldNW},
    # Natural-Width Host-State Fields
    0x00006c00: {'name': 'HOST_CR0', 'c': VMCSFieldNW},
    0x00006c02: {'name': 'HOST_CR3', 'c': VMCSFieldNW},
    0x00006c04: {'name': 'HOST_CR4', 'c': VMCSFieldNW},
    0x00006c06: {'name': 'HOST_FS_BASE', 'c': VMCSFieldNW},
    0x00006c08: {'name': 'HOST_GS_BASE', 'c': VMCSFieldNW},
    0x00006c0a: {'name': 'HOST_TR_BASE', 'c': VMCSFieldNW},
    0x00006c0c: {'name': 'HOST_GDTR_BASE', 'c': VMCSFieldNW},
    0x00006c0e: {'name': 'HOST_IDTR_BASE', 'c': VMCSFieldNW},
    0x00006c10: {'name': 'HOST_IA32_SYSENTER_ESP', 'c': VMCSFieldNW},
    0x00006c12: {'name': 'HOST_IA32_SYSENTER_EIP', 'c': VMCSFieldNW},
    0x00006c14: {'name': 'HOST_RSP', 'c': VMCSFieldNW},
    0x00006c16: {'name': 'HOST_RIP', 'c': VMCSFieldNW},
  }
