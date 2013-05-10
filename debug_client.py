#!/usr/bin/env python

from struct import *

import urwid
import socket, sys

from network import *
from view.gui import Gui
from model.message import *
from server_state_running import ServerStateRunning
from config.config import Config

class BadReply(BaseException):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Unexpected reply message type : %d " % (self.value)

class DebugClient():
  def __init__(self, config):
    # Config
    self.config = config
    # Pointers
    self.network = None
    self.gui = None
  def createComponents(self):
    # Create all the components
    self.messages = Messages()
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
    # create the socket
    self.network.createSocket()
  def run(self):
    self.createComponents()
    self.gui.run()
  def notifyMessage(self, message):
    self.serverState.notifyMessage(message)
  def sendContinue(self):
    m = MessageExecContinue()
    self.network.send(m)
  def notifyUserInput(self, input):
    self.serverState.notifyUserInput(input)
  def setWait(self):
    self.wait = 1
  def endWait(self):
    self.wait = 0
    self.sendContinue()
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

# Debug client main
try: 
  debugClient = DebugClient(Config('config/debug_client.config'))
  debugClient.run()
except BadReply, msg:
  print("%s\n" % (msg))
