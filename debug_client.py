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
    self.run()
  def run(self):
    self.network = Network()
    #self.gui = Gui(self.network)

# Debug client main
debugClient = DebugClient()
