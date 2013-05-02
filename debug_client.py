#!/usr/bin/env python

from struct import *

import urwid
import socket, sys

from network import *
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
    # Running mode
    self.step = 0 # Wait user at every VMExit
    self.mTF = 0 # Monitor Trap Flag is activated
    # User interactions
    self.wait = 0 # We are waiting for a user entry
    self.run()
  def createComponents(self):
    # Create all the components
    self.messages = Messages()
    self.network = Network()
    self.gui = Gui()
    # Share the pointers
    self.gui.network = self.network
    self.gui.debugClient = self
    self.network.debugClient = self
  def run(self):
    self.gui.run()
  def notifyMessage(self, message):
    if self.wait:
      raise BadReply(-1)
    # TODO add the message into the model
    self.messages.append(message)
    message.number = self.messages.length()
    # Handle the message according to the type
    if message.messageType == Message.VMExit:
      # if we are not in step mode we directly continue the execution
      if self.step:
        self.wait = 1
      else:
        self.sendContinue()
    else:
      raise BadReply(message.messageType)
    # Adds here to the model and notifies the view of the changes
    self.gui.notifyMessage(message)
    self.gui.messageFocus(message.number - 1, message)
  def setWait(self):
    self.wait = 1
  def endWait(self):
    self.wait = 0
    self.sendContinue()
  def sendContinue(self):
    m = MessageExecContinue()
    self.network.send(m)
  def notifyUserInput(self, input):
    self.gui.setMinibuf(input)
    if input in ('q', 'Q'):
      raise urwid.ExitMainLoop()
    if input == 's':
      self.step = 1
    if input == 'c':
      self.step = 0
    # We have to notify the debug server that we have finished to wait for user entry
    # execution can continue
    if input in ('s', 'c') and self.wait == 1:
      self.endWait()

# Debug client main
try:
  debugClient = DebugClient()
except BadReply, msg:
  print("%s\n" % (msg))
