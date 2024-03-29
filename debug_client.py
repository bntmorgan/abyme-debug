#!/usr/bin/env python2.7

from struct import *

import urwid
import socket, sys

from network import *
from view.gui import Gui
from model.message import *
from controller.server_state import BadReply, ServerStateRunning, ServerStateMinibuf
from config.config import Config
from model.vmcs import VMCS, VMCSField, VMCSField16
from model.vmm import VMM
import log

class DebugClient():
  VM_NB = 8
  def __init__(self, config):
    # Config
    self.config = config
    # Pointers
    self.network = None
    self.gui = None
    # Models
    self.vmcs = None
    self.core = Core()
    self.serverState = None
    self.vmm = None
    self.vmid = 0
    # flags
    self.step = 0
    self.mTF = 0
    self.vPT = 1 # Enabled in the hypervisor
    self.disass = 0 # Enabled in the hypervisor
  def createComponents(self):
    # Create all the components
    self.messages = []
    self.network = Network()
    self.gui = Gui()
    # Share the pointers
    self.gui.network = self.network
    self.gui.debugClient = self
    self.network.debugClient = self
    # Running mode
    self.endStep() # Wait user at every VMExit
    self.endMTF() # Monitor Trap Flag is desactivated
    # Server state machine : We start with the server running
    self.serverState = ServerStateRunning(self)
    # Create the socket
    self.network.createSocket()
    # Create the models
    self.vmcs = VMCS.createVMCS()
    self.vmm = VMM.createVMM(DebugClient.VM_NB)
  def run(self):
    self.createComponents()
    self.gui.run()
  def notifyMessage(self, message):
    log.log("Receiving %s" % (message.__class__.__name__))
    # XXX appending MessageInfo to a log file
    if message.messageType == Message.Info:
      log.info(message.vmid, message.getString())
    else:
      if message.messageType == Message.CoreRegsData or message.messageType == Message.VMExit:
        # Update debug_client core
        self.core = message.core
      if message.messageType == Message.VMExit:
        self.setVmexit(message.exitReason)
      # Update current executing vmid
      self.setVmid(message.vmid)
      self.addMessage(message)
      self.serverState.notifyMessage(message)
  def sendMessage(self, message):
    log.log("Sending %s" % (message.__class__.__name__))
    self.network.send(message)
    self.addMessage(message)
  def sendContinue(self):
    m = MessageExecContinue()
    self.network.send(m)
    self.addMessage(m)
  def notifyUserInput(self, input):
    self.serverState.notifyUserInput(input)
  def setStep(self):
    self.step = 1
    self.gui.setStep()
  def endStep(self):
    self.step = 0
    self.gui.endStep()
  def setMTF(self):
    self.mTF = 1
    self.gui.setMTF()
  def endMTF(self):
    self.mTF = 0
    self.gui.endMTF()
  def setVPT(self):
    self.vPT = 1
    self.gui.setVPT()
  def endVPT(self):
    self.vPT = 0
    self.gui.endVPT()
  def setDisass(self):
    self.disass = 1
    self.gui.setDisass()
  def endDisass(self):
    self.disass = 0
    self.gui.endDisass()
  def addMessage(self, message):
    self.messages.append(message)
    message.number = len(self.messages) - 1
    # Adds here to the model and notifies the view of the changes
    self.gui.notifyMessage(message)
    self.gui.messageFocus(message.number)
  def info(self, label, text):
    self.addMessage(Info(label, text))
  def setVmid(self, vmid):
    self.vmid = vmid
    self.gui.setVmid(self.vmid, self.core.regs.rip)
  def setVmexit(self, reason):
    self.gui.setVmexit(ExitReason.e[reason & 0xffff]['name'])

# Debug client main
try: 
  if (len(sys.argv) < 2):
    debugClient = DebugClient(Config('config/debug_client.config'))
  else:
    debugClient = DebugClient(Config(sys.argv[1]))
  log.setup(debugClient.config['LOG_PREFIX'])
  log.log('------ STARTUP ------')
  ServerStateMinibuf.restoreHistories()
  debugClient.run()
except BadReply, msg:
  print("%s\n" % (msg))
  log.log(msg, "ERROR")
finally:
  ServerStateMinibuf.saveHistories()
  log.log('------ GOODBYE ------')
  log.logClose()
