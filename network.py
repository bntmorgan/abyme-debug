from struct import *
import socket, sys
import binascii

from model.message import *

class EthernetFrame():
  def __init__(self, packet, ipSrc, ipDst):
    #parse ethernet header
    #headerLength = 14
    #header = packet[:headerLength]
    #eth = unpack('!6s6sH', header)
    #protocol = eth[2]
    # Ethernet
    self.ipDest = ipDst
    self.ipSource = ipSrc
    #self.protocol = protocol
    #self.headerLength = headerLength
    self.payload = packet#[headerLength:]

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
  @staticmethod
  def macStrToBin(mac):
    m = ''
    t = mac.rsplit(':')
    for b in t:
      m += '%c' % (int(b, 16))
    return m
  @staticmethod
  def sendTo(port, data):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.sendto(data, ("192.168.0.2", port))
    sock.close()
  def createSocket(self):
    # Get the ethertype from configuration
    self.ethertype = int(self.debugClient.config['ETHERTYPE'], 16)
    self.macSource = Network.macStrToBin(self.debugClient.config['MAC_SOURCE'])
    self.macDest = Network.macStrToBin(self.debugClient.config['MAC_DEST'])
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.socket.bind(("192.168.0.1", 6666))
    except socket.error , msg:
      print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
      sys.exit()
  def receive(self):
    packet = self.socket.recvfrom(65565)
    # Create ethernet fream object filter protocol
    packet = packet[0]
    frame = EthernetFrame(packet, "192.168.0.2", "192.168.0.1")
    #print frame.macSource
    #if (frame.protocol == self.ethertype):
    self.debugClient.notifyMessage(MessageNetwork.createMessage(frame, 
			frame.payload))
    return 1
  def createFrame(self, payload):
    return self.padding(pack('!6s6sH', self.macDest, self.macSource,
      self.ethertype) + payload)
  def send(self, message):
    payload = message.pack()
    frame = payload#self.createFrame(payload)
    self.socket.sendto(frame, ("192.168.0.2", 6666))
    message.frame = EthernetFrame(frame, "192.168.0.1", "192.168.0.2")
    message.raw = message.frame.payload
  def padding(self, frame):
    minlen = 14 + 42 # size of head plus minimum payload
    l = len(frame)
    if (l < minlen):
      s = "\0" * (minlen - l)
      frame += s
    return frame

