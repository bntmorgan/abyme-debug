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

class VMCSField64(VMCSField):
  def __init__(self, encoding, name):
    VMCSField.__init__(self)
    self.length = 8
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
    f = VMCSField16(0x0000000, 'VIRTUAL_PROCESSOR_ID'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000002, 'POSTED_INT_NOTIF_VECTOR'); vmcs.fields[f.name] = f
    # 16-Bit Guest-State Fields
    f = VMCSField16(0x0000800, 'GUEST_ES_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000802, 'GUEST_CS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000804, 'GUEST_SS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000806, 'GUEST_DS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000808, 'GUEST_FS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x000080A, 'GUEST_GS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x000080C, 'GUEST_LDTR_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x000080E, 'GUEST_TR_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000810, 'GUEST_INTERRUPT_STATUS'); vmcs.fields[f.name] = f
    # 16-Bit Host-State Fields
    f = VMCSField16(0x0000C00, 'HOST_ES_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000C02, 'HOST_CS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000C04, 'HOST_SS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000C06, 'HOST_DS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000C08, 'HOST_FS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000C0A, 'HOST_GS_SELECTOR'); vmcs.fields[f.name] = f
    f = VMCSField16(0x0000C0C, 'HOST_TR_SELECTOR'); vmcs.fields[f.name] = f
    # 64-BIT FIELDS
    # 64-Bit Control Fields
    f = VMCSField64(0x0002000, 'IO_BITMAP_A'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002001, 'IO_BITMAP_A_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002002, 'IO_BITMAP_B'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002003, 'IO_BITMAP_B_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002004, 'MSR_BITMAP'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002005, 'MSR_BITMAP_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002006, 'VM_EXIT_MSR_STORE_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002007, 'VM_EXIT_MSR_STORE_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002008, 'VM_EXIT_MSR_LOAD_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002009, 'VM_EXIT_MSR_LOAD_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000200A, 'VM_ENTRY_MSR_LOAD_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000200B, 'VM_ENTRY_MSR_LOAD_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000200C, 'EXECUTIVE_VMCS_POINTER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000200D, 'EXECUTIVE_VMCS_POINTER_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002010, 'TSC_OFFSET'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002011, 'TSC_OFFSET_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002012, 'VIRTUAL_APIC_PAGE_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002013, 'VIRTUAL_APIC_PAGE_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002014, 'APIC_ACCESS_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002015, 'APIC_ACCESS_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002016, 'POSTED_INTERRUPT_DESCRIPTOR_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002017, 'POSTED_INTERRUPT_DESCRIPTOR_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002018, 'VM_FUNCTION_CONTROLS'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002019, 'VM_FUNCTION_CONTROLS_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000201a, 'EPT_POINTER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000201b, 'EPT_POINTER_HIGHT'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000201c, 'EOI_EXIT0'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000201d, 'EOI_EXIT0_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000201e, 'EOI_EXIT1'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000201f, 'EOI_EXIT1_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002020, 'EOI_EXIT2'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002021, 'EOI_EXIT2_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002022, 'EOI_EXIT3'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002023, 'EOI_EXIT3_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002024, 'EPT_LIST_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002025, 'EPT_LIST_ADDR_HIGH'); vmcs.fields[f.name] = f
    # 64-Bit Read-Only Data Field
    f = VMCSField64(0x0002400, 'GUEST_PHYSICAL_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002401, 'GUEST_PHYSICAL_ADDR_HIGH'); vmcs.fields[f.name] = f
    # 64-Bit Guest-State Fields
    f = VMCSField64(0x0002800, 'GUEST_PHYSICAL_ADDR'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002801, 'GUEST_PHYSICAL_ADDR_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002802, 'VMCS_LINK_POINTER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002803, 'VMCS_LINK_POINTER_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002804, 'GUEST_IA32_DEBUGCTL'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002805, 'GUEST_IA32_DEBUGCTL_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002806, 'GUEST_IA32_PAT'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002807, 'GUEST_IA32_PAT_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002808, 'GUEST_IA32_EFER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002809, 'GUEST_IA32_EFER_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000280a, 'GUEST_IA32_PERF_GLOBAL_CTRL'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000280b, 'GUEST_IA32_PERF_GLOBAL_CTRL_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000280c, 'GUEST_PDPTR0'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000280d, 'GUEST_PDPTR0_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000280e, 'GUEST_PDPTR1'); vmcs.fields[f.name] = f
    f = VMCSField64(0x000280f, 'GUEST_PDPTR1_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002810, 'GUEST_PDPTR2'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002811, 'GUEST_PDPTR2_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002812, 'GUEST_PDPTR3'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002813, 'GUEST_PDPTR3_HIGH'); vmcs.fields[f.name] = f
    # 64-Bit Host-State Fields
    f = VMCSField64(0x0002C00, 'HOST_IA32_PAT'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002C01, 'HOST_IA32_PAT_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002C02, 'HOST_IA32_EFER'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002C03, 'HOST_IA32_EFER_HIGH'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002C04, 'HOST_IA32_PERF_GLOBAL_CTRL'); vmcs.fields[f.name] = f
    f = VMCSField64(0x0002C05, 'HOST_IA32_PERF_GLOBAL_CTRL_HIGH'); vmcs.fields[f.name] = f
    # 32-BIT FIELDS
    # 32-Bit Control Fields
    f = VMCSField32(0x0004000, 'PIN_BASED_VM_EXEC_CONTROL'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004002, 'CPU_BASED_VM_EXEC_CONTROL'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004004, 'EXCEPTION_BITMAP'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004006, 'PAGE_FAULT_ERROR_CODE_MASK'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004008, 'PAGE_FAULT_ERROR_CODE_MATCH'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000400A, 'CR3_TARGET_COUNT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000400C, 'VM_EXIT_CONTROLS'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000400E, 'VM_EXIT_MSR_STORE_COUNT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004010, 'VM_EXIT_MSR_LOAD_COUNT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004012, 'VM_ENTRY_CONTROLS'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004014, 'VM_ENTRY_MSR_LOAD_COUNT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004016, 'VM_ENTRY_INTR_INFO_FIELD'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004018, 'VM_ENTRY_EXCEPTION_ERROR_CODE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000401A, 'VM_ENTRY_INSTRUCTION_LEN'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000401C, 'TPR_THRESHOLD'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000401E, 'SECONDARY_VM_EXEC_CONTROL'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004020, 'PLE_GAP'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004022, 'PLE_WINDOW'); vmcs.fields[f.name] = f
    # 32-Bits Read-Only Data Fields
    f = VMCSField32(0x0004400, 'VM_INSTRUCTION_ERROR'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004402  'VM_EXIT_REASON'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004404, 'VM_EXIT_INTR_INFO'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004406, 'VM_EXIT_INTR_ERROR_CODE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004408, 'IDT_VECTORING_INFO_FIELD'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000440A, 'IDT_VECTORING_ERROR_CODE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000440C, 'VM_EXIT_INSTRUCTION_LEN'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000440E, 'VMX_INSTRUCTION_INFO'); vmcs.fields[f.name] = f
    # 32-Bits Guest-State Fields
    f = VMCSField32(0x0004800, 'GUEST_ES_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004802, 'GUEST_CS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004804, 'GUEST_SS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004806, 'GUEST_DS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004808, 'GUEST_FS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000480A, 'GUEST_GS_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000480C, 'GUEST_LDTR_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000480E, 'GUEST_TR_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004810, 'GUEST_GDTR_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004812, 'GUEST_IDTR_LIMIT'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004814, 'GUEST_ES_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004816, 'GUEST_CS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004818, 'GUEST_SS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000481A, 'GUEST_DS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000481C, 'GUEST_FS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000481E, 'GUEST_GS_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004820, 'GUEST_LDTR_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004822, 'GUEST_TR_AR_BYTES'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004824, 'GUEST_INTERRUPTIBILITY_INFO'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004826, 'GUEST_ACTIVITY_STATE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004828, 'GUEST_SMBASE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000482A, 'GUEST_SYSENTER_CS'); vmcs.fields[f.name] = f
    f = VMCSField32(0x000482E, 'VMX_PREEMPTION_TIMER_VALUE'); vmcs.fields[f.name] = f
    f = VMCSField32(0x0004C00, 'HOST_IA32_SYSENTER_CS'); vmcs.fields[f.name] = f
    # 32-Bits Host-State Fields
  return vmcs
