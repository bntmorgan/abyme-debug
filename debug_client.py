#!/usr/bin/env python

from struct import *

import urwid
import socket, sys

from network import *
from view.gui import Gui
from model.message import *
from controller.server_state import BadReply, ServerStateRunning
from config.config import Config
from model.vmcs import VMCS, VMCSField, VMCSField16
import log

class DebugClient():
  def __init__(self, config):
    # Config
    self.config = config
    # Pointers
    self.network = None
    self.gui = None
    # Models
    self.vmcs = None
    self.core = None
    self.serverState = None
    # flags
    self.mTF = 0
    self.iOBitmaps = 0
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
    self.setStep() # Wait user at every VMExit
    self.endMTF() # Monitor Trap Flag is desactivated
    self.endIOBitmaps() # IOBitmaps are desactivated
    # Server state machine : We start with the server running
    self.serverState = ServerStateRunning(self)
    # Create the socket
    self.network.createSocket()
    # Create the models
    self.vmcs = VMCS.createVMCS()
  def run(self):
    self.createComponents()
    self.gui.run()
  def notifyMessage(self, message):
    log.log("Receiving %s" % (message.__class__.__name__))
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
  def setIOBitmaps(self):
    self.iOBitmaps = 1
  def endIOBitmaps(self):
    self.iOBitmaps = 0
  def addMessage(self, message):
    self.messages.append(message)
    message.number = len(self.messages) - 1
    # Adds here to the model and notifies the view of the changes
    self.gui.notifyMessage(message)
    self.gui.messageFocus(message.number)
  def info(self, label, text):
    self.addMessage(MessageInfo(label, text))
  def cacheExpired(self):
    self.core = None
    self.vmcs = VMCS.createVMCS()

# Debug client main
try: 
  log.log('------ STARTUP ------')
  debugClient = DebugClient(Config('config/debug_client.config'))
  debugClient.run()
except BadReply, msg:
  print("%s\n" % (msg))
  log.log(msg, "ERROR")
finally:
  log.log('------ GOODBYE ------')
  log.logClose()
