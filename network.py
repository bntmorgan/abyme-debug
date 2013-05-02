from struct import *
import socket, sys

from model.message import *

class EthernetFrame():
  def __init__(self, packet):
    #parse ethernet header
    headerLength = 14
    header = packet[:headerLength]
    eth = unpack('!6s6sH', header)
    protocol = socket.ntohs(eth[2])
    # Ethernet
    self.macSource = packet[0:6]
    self.macDest = packet[6:12]
    self.protocol = protocol
    self.headerLength = headerLength

class Network():
  macSource = "\xd4\xbe\xd9\x39\xc8\x46"
  macDest = "\xd4\xbe\xd9\x39\xc8\x46"
  etherType = 0x1234
  def __init__(self):
    self.socket = None
    self.createSocket()
    self.gui = None
  def __del__(self):
    if (self.socket != None):
      self.socket.close()
  def createSocket(self):
    try:
      self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
      #self.socket.bind(("eth0", 0))
    except socket.error , msg:
      print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
      sys.exit()
  def receive(self):
    packet = self.socket.recvfrom(65565)
    # Create ethernet fream object filter protocol
    packet = packet[0]
    frame = EthernetFrame(packet)
    if (frame.protocol == 8):
      self.debugClient.notifyMessage(MessageIn.createMessage(frame))
  def send(self, message):
    payload = message.pack()
    checksum = "\x1a\x2b\x3c\x4d"
    trame = Network.macSource + Network.macDest + pack('!H', socket.htons(Network.ethertype)) + payload + checksum
    self.socket.send(trame)
