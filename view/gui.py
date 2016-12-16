from struct import *

import socket, sys

import urwid
import pprint

from model.message import *
from model.bin import Bin

import log

class Gui():
  banner = """

  _,   ,_,   ,   , ,           
 (_\  //     \  |\/|           
  _)\/'\_     \/| `|           
 '  '    `    ' '  `           
  ,_  _, __ ,  , _,  _,  _,_   
  | \/_,'|_)|  |/ _ / _ /_|_)  
 _|_'\_ _|_'\__'\_|'\_|'\'| \  
'      '       ` _|  _|   '  ` 
                '   '          
"""
#   banner = """                                                                ____                  
#   .--.--.                ,----..                              ,'  , `.                
#  /  /    '.       ,---. /   /   \\                ,---.     ,-+-,.' _ |                
# |  :  /`. /      /__./||   :     :              /__./|  ,-+-. ;   , ||                
# ;  |  |--`  ,---.;  ; |.   |  ;. /         ,---.;  ; | ,--.'|'   |  ;|                
# |  :  ;_   /___/ \\  | |.   ; /--`         /___/ \\  | ||   |  ,', |  ':                
#  \\  \\    `.\\   ;  \\ ' |;   | ;            \\   ;  \\ ' ||   | /  | |  ||                
#   `----.   \\\\   \\  \\: ||   : |             \\   \\  \\: |'   | :  | :  |,                
#   __ \\  \\  | ;   \\  ' ..   | '___           ;   \\  ' .;   . |  ; |--'                 
#  /  /`--'  /  \\   \\   ''   ; : .'|           \\   \\   '|   : |  | ,                    
# '--'.     /    \\   `  ;'   | '/  :            \\   `  ;|   : '  |/                     
#   `--'---'      :   \\ ||   :    /              :   \\ |;   | |`-'                      
#                  '---"  \\   \\ .'                '---" |   ;/                          
#                          `---`                        '---'                           
#       ,---,            ,---,                                                          
#     ,---.'|          ,---.'|            ,--,                                  __  ,-. 
#     |   | :          |   | :          ,'_ /|  ,----._,.  ,----._,.          ,' ,'/ /| 
#     |   | |   ,---.  :   : :     .--. |  | : /   /  ' / /   /  ' /   ,---.  '  | |' | 
#   ,--.__| |  /     \\ :     |,-.,'_ /| :  . ||   :     ||   :     |  /     \\ |  |   ,' 
#  /   ,'   | /    /  ||   : '  ||  ' | |  . .|   | .\\  .|   | .\\  . /    /  |'  :  /   
# .   '  /  |.    ' / ||   |  / :|  | ' |  | |.   ; ';  |.   ; ';  |.    ' / ||  | '    
# '   ; |:  |'   ;   /|'   : |: |:  | : ;  ; |'   .   . |'   .   . |'   ;   /|;  : |    
# |   | '/  ''   |  / ||   | '/ :'  :  `--'   \\`---`-'| | `---`-'| |'   |  / ||  , ;    
# |   :    :||   :    ||   :    |:  ,      .-./.'__/\\_: | .'__/\\_: ||   :    | ---'     
#  \\   \\  /   \\   \\  / /    \\  /  `--`----'    |   :    : |   :    : \\   \\  /           
#   `----'     `----'  `-'----'                 \\   \\  /   \\   \\  /   `----'            
#                                                `--`-'     `--`-'                      
# """
  def __init__(self):
    # XXX
    urwid.ListBox.ignore_focus = True
    # pointers
    self.network = None
    self.debugClient = None
    # graphical components
    self.listMessages = None
    self.listContentMessages = None
    self.listDisplay = None
    self.listContentDisplay = None
    self.title = None
    self.minibuf = None
    self.head = None
    self.top = None
    self.bottomBar = None
    self.execMode = None
    self.mTF = None
    self.vPT = None
    self.disass = None
    self.vmid = None
    self.vmexit = None
    self.palette = [
        ('header', 'white', 'black'),
        ('flags', 'dark cyan', 'black'),
        ('text', 'dark cyan', 'black'),
        ('reveal focus', 'black', 'dark cyan', 'standout')]
    self.initGraphicalComponents()

  def initGraphicalComponents(self):
    self.listContentMessages = urwid.SimpleListWalker([])
    self.listMessages = urwid.ListBox(self.listContentMessages)
    self.listContentDisplay = urwid.SimpleListWalker([])
    self.listDisplay = urwid.ListBox(self.listContentDisplay)
    # List legend
    self.title = urwid.Text("#    N Length Source address    Dest address      Type", wrap='clip')
    head = urwid.AttrMap(self.title, 'header')
    self.minibuf = urwid.Text(": ", wrap='clip')
    bottom = urwid.AttrMap(self.minibuf, 'header')
    self.text = urwid.Text(Gui.banner, align='left')
    self.execMode = urwid.Text("")
    self.setStep()
    self.mTF = urwid.Text("")
    self.vPT = urwid.Text("")
    self.disass = urwid.Text("")
    self.vmid = urwid.Text("",)
    self.vmexit = urwid.Text("")
    self.endMTF()
    self.setVPT()
    self.endDisass()
    self.setVmid(0, 0)
    widgetsColumns = [
        (5, urwid.AttrMap(self.execMode, 'flags')),
        (5, urwid.AttrMap(self.mTF, 'flags')),
        (5, urwid.AttrMap(self.vPT, 'flags')),
        (5, urwid.AttrMap(self.disass, 'flags')),
        (22, urwid.AttrMap(self.vmid, 'flags')),
        (22, urwid.AttrMap(self.vmexit, 'flags'))]
    self.bottomBar = urwid.Columns(widgetsColumns)
    widgetsPile = [
        urwid.Frame(self.listMessages, head, bottom),
        self.listDisplay,
        (1, urwid.Filler(self.bottomBar))]
    self.top = urwid.Pile(widgetsPile);
    urwid.connect_signal(self.listContentMessages, "modified", self.listMessagesModified)
    urwid.connect_signal(self.listContentDisplay, "modified", self.listDisplayModified)
  def setTitle(self, title):
    self.title.set_text(title)
  def setMinibuf(self, minibuf):
    self.minibuf.set_text(": %s" % (minibuf))
  def run(self):
    loop = urwid.MainLoop(self.top, self.palette,
        input_filter=self.filterInput, unhandled_input=self.exitOnCr)
    loop.watch_file(self.network.socket, self.network.receive)
    try:
      loop.run()
    except KeyboardInterrupt:
      sys.exit(0)
  def notifyMessage(self, message):
    t = urwid.Text(message.format())
    # Add the message to the list
    self.listContentMessages.append(urwid.AttrMap(t, None, 'reveal focus'))
  def listDisplayModified(self):
    pass
  def listMessagesModified(self):
    m = self.debugClient.messages[self.debugClient.gui.listMessages.focus_position]
    if isinstance(m, MessageMemoryData) and self.debugClient.disass:
      b = Bin(m.data, m.address, self.debugClient.core.getMode())
      self.debugClient.gui.display(b.disasm())
      b = None
    else:
      self.display(m.formatFull())
    self.setMinibuf("%d" % (self.listMessages.focus_position))
  def messageFocus(self, number):
    # Refresh focus
    if len(self.debugClient.messages) > number and number >= 0:
      self.listMessages.focus_position = number
  def focusMinibuf(self):
    self.top.focus_position = 2
  def focusDisplay(self):
    self.top.focus_position = 1
  def focusList(self):
    self.top.focus_position = 0
  def messageDisplayInc(self):
    log.log("Display Inc")
    if self.listDisplay.focus_position < len(self.listContentDisplay) - 1:
      self.listDisplay.focus_position += 1
      # self.focusDisplay()
  def messageDisplayDec(self):
    log.log("Display Dec")
    if self.listDisplay.focus_position > 0:
      self.listDisplay.focus_position -= 1
      # self.focusDisplay()
  def messageFocusInc(self):
    log.log("Inc")
    if len(self.debugClient.messages) > 0 and self.listMessages.focus_position < len(self.debugClient.messages) - 1:
      self.listMessages.focus_position += 1
    self.focusList()
  def messageFocusDec(self):
    log.log("Dec")
    if len(self.debugClient.messages) > 0 and self.listMessages.focus_position > 0:
      self.listMessages.focus_position -= 1
    self.focusList()
  def exitOnCr(self,  input):
    self.debugClient.notifyUserInput(input)
    return True
  def filterInput(self, input, raw):
    log.log("Filter !!!! %s" % (input))
    if (input == 'up' or input == 'down'):
      return None
    return input
  def display(self, text):
    while len(self.listContentDisplay) > 0 : self.listContentDisplay.pop()
    for i in text.split('\n'):
      self.listContentDisplay.append(urwid.AttrMap(urwid.Text(i), None, 'reveal focus'))
  def setStep(self):
    self.execMode.set_text("[STP]")
  def endStep(self):
    self.execMode.set_text(" STP ")
  def setMTF(self):
    self.mTF.set_text("[MTF]")
  def endMTF(self):
    self.mTF.set_text(" MTF ")
  def setVPT(self):
    self.vPT.set_text("[VPT]")
  def endVPT(self):
    self.vPT.set_text(" VPT ")
  def setDisass(self):
    self.disass.set_text("[DIS]")
  def endDisass(self):
    self.disass.set_text(" DIS ")
  def setVmid(self, vmid, rip):
    self.vmid.set_text("{%d@0x%016x}" % (vmid, rip))
  def setVmexit(self, reason):
    self.vmexit.set_text("{%s}" % (reason))

