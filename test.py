#!/usr/bin/env python2.7

from network import *
from config.config import Config
from model.message import *
import log

class DebugClientShell(object):
  def __init__(self, config):
    self.config = config

class Test():
  def __init__(self, config):
    # Fake debug client for network
    self.debugClientShell = None
    # Config
    self.config = config
    # Pointers
    self.network = None
  def createComponents(self):
    # Revers the client mac config
    tm = self.config['MAC_SOURCE']
    self.config['MAC_SOURCE'] = self.config['MAC_DEST']
    self.config['MAC_DEST'] = tm
    # Fake debug client for network
    self.debugClientShell = DebugClientShell(self.config)
    # Create network
    self.network = Network()
    self.network.debugClient = self.debugClientShell
    # Create the socket
    self.network.createSocket()
  def run(self):
    self.testMessageInfo()
  def testMessageInfo(self):
    m = MessageInfo()
    s = "Anticonstitutionnel\n"
    m.length = len(s)
    m.data = s
    frame = self.network.createFrame(m.pack() + pack('Q', m.length) + m.data)
    self.network.socket.send(frame)


# Debug client main
log.fd.close()
log.fd = open("test_log", "w")
log.log('------ STARTUP ------')
test = Test(Config('config/debug_client.config'))
test.createComponents()
test.run()
log.log('------ GOODBYE ------')
