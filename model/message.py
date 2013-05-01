from struct import *

import socket, sys

class Message():
  def __init__(self, packet):
    #parse ethernet header
    ethLength = 14
    ethHeader = packet[:ethLength]
    eth = unpack('!6s6sH' , ethHeader)
    ethProtocol = socket.ntohs(eth[2])
    # Ethernet
    self.ethMacSource = packet[0:6]
    self.ethMacDest = packet[6:12]
    self.ethProtocol = ethProtocol
    self.ethLength = ethLength
    # Debug protocol XXX
    self.messageType = 0
    # GUI
    self.new = 1
  @staticmethod
  def ethAddr (a):
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
    return b
  def format(self):
    n = "N" if self.new else " "
    t = "VM exit"
    l = "%04d B" % (self.ethLength)
    # new length addrSource addrDest type
    return "%s %s %s %s %s" % (n, l, Message.ethAddr(self.ethMacSource), Message.ethAddr(self.ethMacDest), t)
