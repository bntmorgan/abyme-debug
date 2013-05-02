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
    protocol = socket.ntohs(eth[2])
    # Ethernet
    self.macSource = packet[0:6]
    self.macDest = packet[6:12]
    self.protocol = protocol
    self.headerLength = headerLength
    self.payload = packet[headerLength:]

class Network():
  macSource = "\xd4\xbe\xd9\x39\xc8\x46"
  macDest = "\xd4\xbe\xd9\x39\xc8\x46"
  #macSource = "\xff\xff\xff\xff\xff\xff"
  #macDest = "\xff\xff\xff\xff\xff\xff"
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
      #self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
      self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
      self.socket.bind(("eth0", 0))
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
    frame = Network.macDest + Network.macSource + pack('!H', Network.etherType) + payload
    checksum = binascii.crc32(frame)
    # print("%02x:%02x:%02x:%02x:%02x:%02x" % (ord(frame[0]), ord(frame[1]), ord(frame[2]), ord(frame[3]), ord(frame[4]), ord(frame[5])))
    # print("%02x:%02x:%02x:%02x:%02x:%02x" % (ord(frame[6]), ord(frame[7]), ord(frame[8]), ord(frame[9]), ord(frame[10]), ord(frame[11])))
    # print("%x%x" % (ord(frame[12]), ord(frame[13])))
    # print("%x" % (ord(frame[14])))
    # print("0x%08x" % (checksum))
    frame = self.padding(frame)
    # print("ENVOYE %d\n" % (self.socket.send(frame + pack('l', checksum))))
    self.socket.send(frame + pack('l', checksum))
  def padding(self, frame):
    minlen = 14 + 42 # size of head plus minimum payload
    l = len(frame)
    if (l < minlen):
      s = "\0" * (minlen - l)
      frame += s
      print('padding lol %s len %d minlen %d %d' % (s, l, minlen, (minlen - l))) 
    return frame

