#!/usr/bin/env python2.7

from network import *
from config.config import Config
from model.message import *
import log

class DebugClientShell(object):
  def __init__(self, config):
    self.config = config
    self.message = None
  def notifyMessage(self, message):
    self.message = message

class Test():
  def __init__(self, config):
    # Fake debug client for network
    self.debugClient = None
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
    self.debugClient = DebugClientShell(self.config)
    # Create network
    self.network = Network()
    self.network.debugClient = self.debugClient
    # Create the socket
    self.network.createSocket()
  def run(self):
    self.testMessageInfo()
    self.testMessageNetboot()
  def testMessageInfo(self):
    m = MessageInfo()
    s = "Anticonstitutionnel\n"
    m.vmid = 0
    m.length = len(s)
    m.data = s
    frame = self.network.createFrame(m.pack() + pack('Q', m.length) + m.data)
    self.network.socket.send(frame)
  def testMessageNetboot(self):
    m = MessageNetboot()
    m.vmid = 0
    frame = self.network.createFrame(m.pack())
    self.network.socket.send(frame)
    # Waiting for data
    while True:
      self.network.receive()
      message = self.debugClient.message
      # Test type
      if not isinstance(message, MessageMemoryWrite):
        raise BadReply(message.messageType)
      length = message.length
      log.log("Receiving 0x%x bytes" % (length))
      # Send Commit message
      m = MessageCommit()
      m.vmid = 0
      m.ok = 1
      frame = self.network.createFrame(m.pack() + pack('B', m.ok))
      self.network.socket.send(frame)
      if length == 0:
        log.log("Uploading ended")
        break

# Debug client main
log.setup("test_")
log.log('------ STARTUP ------')
test = Test(Config('config/debug_client.config'))
test.createComponents()
test.run()
log.log('------ GOODBYE ------')
