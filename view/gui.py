from struct import *

import socket, sys

import urwid

from model.message import Message

class Gui():
  banner = """
 ____ __     __ ____                                                                                
/ ___|\ \   / // ___|                                                                               
\___ \ \ \ / /| |                                                                                   
 ___) | \ V / | |___                                                                                
|____/   \_/   \____|                                                                               
                                                                                                    
                                                                                                    
__     __ ___  ____  _____  _   _    _     _        __  __     _     ____  _   _  ___  _   _  _____ 
\ \   / /|_ _||  _ \|_   _|| | | |  / \   | |      |  \/  |   / \   / ___|| | | ||_ _|| \ | || ____|
 \ \ / /  | | | |_) | | |  | | | | / _ \  | |      | |\/| |  / _ \ | |    | |_| | | | |  \| ||  _|  
  \ V /   | | |  _ <  | |  | |_| |/ ___ \ | |___   | |  | | / ___ \| |___ |  _  | | | | |\  || |___ 
   \_/   |___||_| \_\ |_|   \___//_/   \_\|_____|  |_|  |_|/_/   \_\\\\____||_| |_||___||_| \_||_____|
                                                                                                    
                                                                                                    
 ____   _____  ____   _   _   ____   ____  _____  ____                                              
|  _ \ | ____|| __ ) | | | | / ___| / ___|| ____||  _ \                                             
| | | ||  _|  |  _ \ | | | || |  _ | |  _ |  _|  | |_) |                                            
| |_| || |___ | |_) || |_| || |_| || |_| || |___ |  _ <                                             
|____/ |_____||____/  \___/  \____| \____||_____||_| \_\       
"""
  def __init__(self):
    # pointers
    self.network = None
    self.debugClient = None
    # graphical components
    self.listContent = None
    self.title = None
    self.minibuffer = None
    self.listbox = None
    self.head = None
    self.top = None
    self.text = None
    self.bottomBar = None
    self.execMode = None
    self.mTF = None
    self.palette = [
        ('header', 'white', 'black'),
        ('flags', 'dark cyan', 'black'),
        ('text', 'dark cyan', 'black'),
        ('reveal focus', 'black', 'dark cyan', 'standout')]
    self.initGraphicalComponents()
  def initGraphicalComponents(self):
    self.listContent = urwid.SimpleListWalker([])
    self.listbox = urwid.ListBox(self.listContent)
    # List legend
    self.title = urwid.Text("#    N Length Source address    Dest address      Type", wrap='clip')
    head = urwid.AttrMap(self.title, 'header')
    self.minibuf = urwid.Text(": ", wrap='clip')
    bottom = urwid.AttrMap(self.minibuf, 'header')
    self.text = urwid.Text(Gui.banner, align='left')
    self.execMode = urwid.Text("")
    self.setStep()
    self.mTF = urwid.Text("")
    self.endMTF()
    widgetsColumns = [
        (9, urwid.AttrMap(self.execMode, 'flags')), 
        (10, urwid.AttrMap(self.mTF, 'flags'))]
    self.bottomBar = urwid.Columns(widgetsColumns)
    widgetsPile = [
        urwid.Frame(self.listbox, head, bottom),
        urwid.AttrMap(urwid.Filler(self.text, valign = 'top'), 'text'),
        (1, urwid.Filler(self.bottomBar))]
    self.top = urwid.Pile(widgetsPile);
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
  def messageFocus(self, number, message):
    # Refresh focus
    self.listbox.set_focus(number)
    # Refresh text content
    self.display(message.formatFull())
    self.setMinibuf("%s" % (number))
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

