#!/usr/bin/env python

from struct import *

import urwid
import socket, sys

from network import Network
from view.gui import Gui

class DebugClient():
  def __init__(self):
    self.network = None
    self.gui = None
    self.createComponents()
    self.run()
    # Running mode
    self.step = 1
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

# Debug client main
debugClient = DebugClient()
