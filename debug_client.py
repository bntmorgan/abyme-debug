#!/usr/bin/env python

from struct import *

import urwid
import socket, sys

from network import Network
from view.gui import Gui
from model.message import *

class BadReply(BaseException):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return "Unexpected reply message type : %d " % (self.value)

class DebugClient():
  def __init__(self):
    self.network = None
    self.gui = None
    self.createComponents()
    self.run()
    # Running mode
    self.step = 1 # Wait user at every VMExit
    self.mTF = 0 # Monitor Trap Flag is activated
    # User interactions
    self.wait = 0 # We are waiting for a user entry
  def createComponents(self):
    # Create all the components
    self.network = Network()
    self.gui = Gui()
    # Share the pointers
    self.gui.network = self.network
    self.gui.debugClient = self
    self.network.gui = self.gui
    self.network.debugClient = self
  def run(self):
    self.gui.run()
  def notifyMessage(self, message):
    # Adds here to the model and notifies the view of the changes
    self.gui.notifyMessage(message)
    # TODO add the message into the model
    # Handle the message according to the type
    if message.messageType == Message.VMExit:
      # if we are not in step mode we directly continue the execution
      if self.step:
        self.wait = 1
      else:
        self.sendContinue()
    else:
      raise BadReply(message.messageType)
  def setWait():
    self.wait = 1
  def endWait():
    self.wait = 0
    self.sendContinue()
  def sendContinue():
    m = MessageExecContinue()
    self.network.send(m)


# Debug client main
try:
  debugClient = DebugClient()
except BaseException, msg:
  print("%s\n" % (msg))
