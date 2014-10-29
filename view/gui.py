from struct import *

import socket, sys

import urwid

from model.message import Message

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
    # pointers
    self.network = None
    self.debugClient = None
    # graphical components
    self.listContent = None
    self.title = None
    self.minibuf = None
    self.listBox = None
    self.head = None
    self.top = None
    self.text = None
    self.bottomBar = None
    self.execMode = None
    self.mTF = None
    self.vPT = None
    self.palette = [
        ('header', 'white', 'black'),
        ('flags', 'dark cyan', 'black'),
        ('text', 'dark cyan', 'black'),
        ('reveal focus', 'black', 'dark cyan', 'standout')]
    self.initGraphicalComponents()

  def initGraphicalComponents(self):
    self.listContent = urwid.SimpleListWalker([])
    self.listBox = urwid.ListBox(self.listContent)
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
    self.endMTF()
    self.setVPT()
    widgetsColumns = [
        (9, urwid.AttrMap(self.execMode, 'flags')), 
        (10, urwid.AttrMap(self.mTF, 'flags')),
        (11, urwid.AttrMap(self.vPT, 'flags'))]
    self.bottomBar = urwid.Columns(widgetsColumns)
    widgetsPile = [
        urwid.Frame(self.listBox, head, bottom),
        urwid.AttrMap(urwid.Filler(self.text, valign = 'top'), 'text'),
        (1, urwid.Filler(self.bottomBar))]
    self.top = urwid.Pile(widgetsPile);
    urwid.connect_signal(self.listContent, "modified", self.listBoxModified)
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
    self.listContent.append(urwid.AttrMap(t, None, 'reveal focus'))
  def listBoxModified(self):
    self.display(self.debugClient.messages[self.listBox.focus_position].formatFull())
    self.setMinibuf("%d" % (self.listBox.focus_position))
  def messageFocus(self, number):
    # Refresh focus
    if len(self.debugClient.messages) > number and number >= 0:
      self.listBox.focus_position = number
  def focusMinibuf(self):
    self.top.focus_position = 2
  def focusList(self):
    self.top.focus_position = 0
  def messageFocusInc(self):
    log.log("Inc")
    if len(self.debugClient.messages) > 0 and self.listBox.focus_position < len(self.debugClient.messages) - 1:
      self.focusList()
      self.listBox.focus_position += 1
  def messageFocusDec(self):
    log.log("Dec")
    if len(self.debugClient.messages) > 0 and self.listBox.focus_position > 0:
      self.focusList()
      self.listBox.focus_position -= 1
  def exitOnCr(self,  input):
    self.debugClient.notifyUserInput(input)
  def filterInput(self, input, raw):
    return input
  def display(self, text):
    self.text.set_text(text)
  def setStep(self):
    self.execMode.set_text("MODE : S")
  def endStep(self):
    self.execMode.set_text("MODE : C")
  def setMTF(self):
    self.mTF.set_text("MTF : ON ")
  def endMTF(self):
    self.mTF.set_text("MTF : OFF")
  def setVPT(self):
    self.vPT.set_text("VPT : ON ")
  def endVPT(self):
    self.vPT.set_text("VPT : OFF")

