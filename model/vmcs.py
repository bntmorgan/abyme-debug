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
    # 64-Bit COntrol Fields
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

    return vmcs
