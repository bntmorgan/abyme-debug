from struct import *
import socket, sys

from model.message import Message

class Network():
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
    except socket.error , msg:
      print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
      sys.exit()
  def receive(self):
    packet = self.socket.recvfrom(65565)
    # packet string from tuple XXX
    # ne pas faire deux fois...
    packet = packet[0]
    ethLength = 14
    ethHeader = packet[:ethLength]
    eth = unpack('!6s6sH' , ethHeader)
    ethProtocol = socket.ntohs(eth[2])
    if (ethProtocol == 8):
      self.gui.notifyMessage(Message(packet))
