class VMCSField(object):
  def __init__(self):
    self.length = 0
    self.encoding = 0
    self.name = ''
    self.value = 0

class VMCSField16(VMCSField):
  def __init__(self, encoding, name):
    VMCSField.__init__(self)
    self.length = 2
    self.encoding = encoding
    self.name = name

class VMCSField32(VMCSField):
  def __init__(self, encoding, name):
    VMCSField.__init__(self)
    self.length = 4
    self.encoding = encoding
    self.name = name

class VMCSField64(VMCSField):
  def __init__(self, encoding, name):
    VMCSField.__init__(self)
    self.length = 8
    self.encoding = encoding
    self.name = name

class VMCSFieldNW(VMCSField):
  def __init__(self, encoding, name):
    VMCSField.__init__(self)
    self.length = 4
    self.encoding = encoding
    self.name = name

class VMCS(object):
  def __init__(self):
    # XXX
    self.core = None
    self.fields = {}
  @staticmethod
  def createVMCS(core = None):
    vmcs = VMCS()
    f = None
    # create the dict
    # 16-BIT FIELDS
    # 16-Bit Control Fields
    f = VMCSField16(0x00000000, 'VIRTUAL_PROCESSOR_ID'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000002, 'POSTED_INT_NOTIF_VECTOR'); vmcs.fields[f.name] = f
    # 16-Bit Guest-State Fields
    f = VMCSField16(0x00000800, 'GUEST_ES_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000802, 'GUEST_CS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000804, 'GUEST_SS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000806, 'GUEST_DS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000808, 'GUEST_FS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000080A, 'GUEST_GS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000080C, 'GUEST_LDTR_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000080E, 'GUEST_TR_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000810, 'GUEST_INTERRUPT_STATUS'); vmcs.fields[f.name] = f
    # 16-Bit Host-State Fields
    f = VMCSField16(0x00000C00, 'HOST_ES_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000C02, 'HOST_CS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000C04, 'HOST_SS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000C06, 'HOST_DS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000C08, 'HOST_FS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000C0A, 'HOST_GS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x00000C0C, 'HOST_TR_SELECTOR'); vmcs.fields[f.name] = f
    # 64-BIT FIELDS
    # 64-Bit Control Fields
    f = VMCSField64(0x00002000, 'IO_BITMAP_A'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002001, 'IO_BITMAP_A_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002002, 'IO_BITMAP_B'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002003, 'IO_BITMAP_B_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002004, 'MSR_BITMAP'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002005, 'MSR_BITMAP_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002006, 'VM_EXIT_MSR_STORE_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002007, 'VM_EXIT_MSR_STORE_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002008, 'VM_EXIT_MSR_LOAD_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002009, 'VM_EXIT_MSR_LOAD_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000200A, 'VM_ENTRY_MSR_LOAD_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000200B, 'VM_ENTRY_MSR_LOAD_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000200C, 'EXECUTIVE_VMCS_POINTER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000200D, 'EXECUTIVE_VMCS_POINTER_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002010, 'TSC_OFFSET'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002011, 'TSC_OFFSET_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002012, 'VIRTUAL_APIC_PAGE_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002013, 'VIRTUAL_APIC_PAGE_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002014, 'APIC_ACCESS_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002015, 'APIC_ACCESS_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002016, 'POSTED_INTERRUPT_DESCRIPTOR_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002017, 'POSTED_INTERRUPT_DESCRIPTOR_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002018, 'VM_FUNCTION_CONTROLS'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002019, 'VM_FUNCTION_CONTROLS_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000201A, 'EPT_POINTER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000201B, 'EPT_POINTER_HIGHT'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000201C, 'EOI_EXIT0'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000201D, 'EOI_EXIT0_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000201E, 'EOI_EXIT1'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000201F, 'EOI_EXIT1_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002020, 'EOI_EXIT2'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002021, 'EOI_EXIT2_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002022, 'EOI_EXIT3'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002023, 'EOI_EXIT3_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002024, 'EPT_LIST_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002025, 'EPT_LIST_ADDR_HIGH'); vmcs.fields[f.name] = f
    # 64-Bit Read-Only Data Field
    f = VMCSField64(0x00002400, 'GUEST_PHYSICAL_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002401, 'GUEST_PHYSICAL_ADDR_HIGH'); vmcs.fields[f.name] = f
    # 64-Bit Guest-State Fields
    f = VMCSField64(0x00002800, 'GUEST_PHYSICAL_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002801, 'GUEST_PHYSICAL_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002802, 'VMCS_LINK_POINTER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002803, 'VMCS_LINK_POINTER_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002804, 'GUEST_IA32_DEBUGCTL'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002805, 'GUEST_IA32_DEBUGCTL_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002806, 'GUEST_IA32_PAT'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002807, 'GUEST_IA32_PAT_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002808, 'GUEST_IA32_EFER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002809, 'GUEST_IA32_EFER_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000280A, 'GUEST_IA32_PERF_GLOBAL_CTRL'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000280B, 'GUEST_IA32_PERF_GLOBAL_CTRL_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000280C, 'GUEST_PDPTR0'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000280D, 'GUEST_PDPTR0_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000280E, 'GUEST_PDPTR1'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0000280F, 'GUEST_PDPTR1_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002810, 'GUEST_PDPTR2'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002811, 'GUEST_PDPTR2_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002812, 'GUEST_PDPTR3'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002813, 'GUEST_PDPTR3_HIGH'); vmcs.fields[f.name] = f
    # 64-Bit Host-State Fields
    f = VMCSField64(0x00002C00, 'HOST_IA32_PAT'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002C01, 'HOST_IA32_PAT_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002C02, 'HOST_IA32_EFER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002C03, 'HOST_IA32_EFER_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002C04, 'HOST_IA32_PERF_GLOBAL_CTRL'); vmcs.fields[f.name] = f
    f = VMCSField64(0x00002C05, 'HOST_IA32_PERF_GLOBAL_CTRL_HIGH'); vmcs.fields[f.name] = f
    # 32-BIT FIELDS
    # 32-Bit Control Fields
    f = VMCSField32(0x00004000, 'PIN_BASED_VM_EXEC_CONTROL'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004002, 'CPU_BASED_VM_EXEC_CONTROL'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004004, 'EXCEPTION_BITMAP'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004006, 'PAGE_FAULT_ERROR_CODE_MASK'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004008, 'PAGE_FAULT_ERROR_CODE_MATCH'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000400A, 'CR3_TARGET_COUNT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000400C, 'VM_EXIT_CONTROLS'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000400E, 'VM_EXIT_MSR_STORE_COUNT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004010, 'VM_EXIT_MSR_LOAD_COUNT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004012, 'VM_ENTRY_CONTROLS'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004014, 'VM_ENTRY_MSR_LOAD_COUNT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004016, 'VM_ENTRY_INTR_INFO_FIELD'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004018, 'VM_ENTRY_EXCEPTION_ERROR_CODE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000401A, 'VM_ENTRY_INSTRUCTION_LEN'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000401C, 'TPR_THRESHOLD'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000401E, 'SECONDARY_VM_EXEC_CONTROL'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004020, 'PLE_GAP'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004022, 'PLE_WINDOW'); vmcs.fields[f.name] = f
    # 32-Bits Read-Only Data Fields
    f = VMCSField32(0x00004400, 'VM_INSTRUCTION_ERROR'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004402, 'VM_EXIT_REASON'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004404, 'VM_EXIT_INTR_INFO'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004406, 'VM_EXIT_INTR_ERROR_CODE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004408, 'IDT_VECTORING_INFO_FIELD'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000440A, 'IDT_VECTORING_ERROR_CODE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000440C, 'VM_EXIT_INSTRUCTION_LEN'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000440E, 'VMX_INSTRUCTION_INFO'); vmcs.fields[f.name] = f
    # 32-Bits Guest-State Fields
    f = VMCSField32(0x00004800, 'GUEST_ES_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004802, 'GUEST_CS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004804, 'GUEST_SS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004806, 'GUEST_DS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004808, 'GUEST_FS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000480A, 'GUEST_GS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000480C, 'GUEST_LDTR_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000480E, 'GUEST_TR_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004810, 'GUEST_GDTR_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004812, 'GUEST_IDTR_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004814, 'GUEST_ES_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004816, 'GUEST_CS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004818, 'GUEST_SS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000481A, 'GUEST_DS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000481C, 'GUEST_FS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000481E, 'GUEST_GS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004820, 'GUEST_LDTR_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004822, 'GUEST_TR_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004824, 'GUEST_INTERRUPTIBILITY_INFO'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004826, 'GUEST_ACTIVITY_STATE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x00004828, 'GUEST_SMBASE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000482A, 'GUEST_SYSENTER_CS'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0000482E, 'VMX_PREEMPTION_TIMER_VALUE'); vmcs.fields[f.name] = f
    # 32-Bits Host-State Fields
    f = VMCSField32(0x00004C00, 'HOST_IA32_SYSENTER_CS'); vmcs.fields[f.name] = f
    # NATURAL-WIDTH FIELDS
    # Natural-Width Control Fields
    f = VMCSFieldNW(0x00006000, 'CR0_GUEST_HOST_MASK'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006002, 'CR4_GUEST_HOST_MASK'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006004, 'CR0_READ_SHADOW'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006006, 'CR4_READ_SHADOW'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006008, 'CR3_TARGET_VALUE0'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000600a, 'CR3_TARGET_VALUE1'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000600c, 'CR3_TARGET_VALUE2'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000600e, 'CR3_TARGET_VALUE3'); vmcs.fields[f.name] = f
    # Natural-Width Read-Only Data Fields
    f = VMCSFieldNW(0x00006400, 'EXIT_QUALIFICATION'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006402, 'IO_RCX'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006404, 'IO_RSI'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006406, 'IO_RDI'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006408, 'IO_RIP'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000640a, 'GUEST_LINEAR_ADDRESS'); vmcs.fields[f.name] = f
    # Natural-Width Guest-State Fields
    f = VMCSFieldNW(0x00006800, 'GUEST_CR0'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006802, 'GUEST_CR3'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006804, 'GUEST_CR4'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006806, 'GUEST_ES_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006808, 'GUEST_CS_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000680a, 'GUEST_SS_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000680c, 'GUEST_DS_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000680e, 'GUEST_FS_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006810, 'GUEST_GS_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006812, 'GUEST_LDTR_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006814, 'GUEST_TR_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006816, 'GUEST_GDTR_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006818, 'GUEST_IDTR_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000681a, 'GUEST_DR7'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000681c, 'GUEST_RSP'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x0000681e, 'GUEST_RIP'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006820, 'GUEST_RFLAGS'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006822, 'GUEST_PENDING_DBG_EXCEPTIONS'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006824, 'GUEST_SYSENTER_ESP'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006826, 'GUEST_SYSENTER_EIP'); vmcs.fields[f.name] = f
    # Natural-Width Host-State Fields
    f = VMCSFieldNW(0x00006c00, 'HOST_CR0'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c02, 'HOST_CR3'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c04, 'HOST_CR4'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c06, 'HOST_FS_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c08, 'HOST_GS_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c0a, 'HOST_TR_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c0c, 'HOST_GDTR_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c0e, 'HOST_IDTR_BASE'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c10, 'HOST_IA32_SYSENTER_ESP'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c12, 'HOST_IA32_SYSENTER_EIP'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c14, 'HOST_RSP'); vmcs.fields[f.name] = f
    f = VMCSFieldNW(0x00006c16, 'HOST_RIP'); vmcs.fields[f.name] = f
    return vmcs
