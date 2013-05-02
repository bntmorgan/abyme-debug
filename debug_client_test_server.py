#!/usr/bin/env python

from struct import *

import socket, sys
import time

from network import Network
from model.message import *

class DebugClient():
  def __init__(self):
    self.network = Network()
    self.network.debugClient = self
    self.wait = 1
    self.runTest()
  def runTest(self):
    m = MessageVMExit()
    m.exitReason = 30
    while(1):
      self.wait = 1
      self.network.send(m) 
      print("sent\n")
      while(self.wait):
        self.wait = not(self.network.receive())
      time.sleep(2)
  def notifyMessage(self, message):
    print("Message received")
    print("Type %d" % (message.messageType))

dc = DebugClient()
