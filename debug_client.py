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
from log import log, logClose

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
    self.endMTF() # Monitor Trap Flag is activated
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
    self.addMessage(message)
    self.serverState.notifyMessage(message)
  def sendMessage(self, message):
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
  debugClient = DebugClient(Config('config/debug_client.config'))
  debugClient.run()
except BadReply, msg:
  logClose()
  print("%s\n" % (msg))
