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
  def createComponents(self):
    # Create all the components
    self.network = Network()
    self.gui = Gui()
    # Share the pointers
    self.gui.network = self.network
  def run(self):
    self.gui.run()

# Debug client main
debugClient = DebugClient()
