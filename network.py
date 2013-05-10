from struct import *
import socket, sys
import binascii

from model.message import *

class EthernetFrame():
  def __init__(self, packet):
    #parse ethernet header
    headerLength = 14
    header = packet[:headerLength]
    eth = unpack('!6s6sH', header)
    protocol = eth[2]
    # Ethernet
    self.macSource = packet[0:6]
    self.macDest = packet[6:12]
    self.protocol = protocol
    self.headerLength = headerLength
    self.payload = packet[headerLength:]

class Network():
  def __init__(self):
    self.socket = None
    self.debugClient = None
    self.ethertype = None
    self.macSource = None
    self.macDest = None
  def __del__(self):
    if (self.socket != None):
      self.socket.close()
  def createSocket(self):
    # Get the ethertype from configuration
    self.ethertype = int(self.debugClient.config['ETHERTYPE'], 16)
    self.macSource = self.debugClient.config['MAC_SOURCE']
    self.macDest = self.debugClient.config['MAC_DEST']
    try:
      self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
      self.socket.bind((self.debugClient.config['IF'], 0))
    except socket.error , msg:
      print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
      sys.exit()
  def receive(self):
    packet = self.socket.recvfrom(65565)
    # Create ethernet fream object filter protocol
    packet = packet[0]
    frame = EthernetFrame(packet)
    if (frame.protocol == self.ethertype):
      self.debugClient.notifyMessage(Message.createMessage(frame))
      return 1
    return 0
  def send(self, message):
    payload = message.pack()
    checksum = "\x1a\x2b\x3c\x4d"
    frame = self.macDest + self.macSource + pack('!H', self.ethertype) + payload
    checksum = binascii.crc32(frame)
    frame = self.padding(frame)
    self.socket.send(frame + pack('l', checksum))
  def padding(self, frame):
    minlen = 14 + 42 # size of head plus minimum payload
    l = len(frame)
    if (l < minlen):
      s = "\0" * (minlen - l)
      frame += s
    return frame

