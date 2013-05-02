#!/usr/bin/env python

from struct import *

import socket, sys
import time

from network import Network
from model.message import *

class DebugClient():
  def __init__(self):
    self.network = Network()
    self.runTest()
  def runTest(self):
    m = MessageVMExit()
    while(1):
      self.network.send(m) 
      print("sent\n")
      time.sleep(2)

dc = DebugClient()
