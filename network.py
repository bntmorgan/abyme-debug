from struct import *
import socket, sys

class Network():
  def __init__(self):
    self.socket = None
    self.createSocket()
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
    #packet string from tuple
    packet = packet[0]
    #parse ethernet header
    eth_length = 14
    eth_header = packet[:eth_length]
    eth = unpack('!6s6sH' , eth_header)
    eth_protocol = socket.ntohs(eth[2])
    if (eth_protocol == 8):
      #t = urwid.Text('Destination MAC : ' + self.eth_addr(packet[0:6]) + ' Source MAC : ' + self.eth_addr(packet[6:12]) + ' Protocol : ' + str(eth_protocol))
      return 'lol'
    return ''
  def eth_addr (self, a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
    return b
