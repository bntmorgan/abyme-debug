from struct import *

import socket, sys

import urwid

from model.message import Message

class Gui():
  def __init__(self):
    # pointers
    self.network = None
    # graphical components
    self.listContent = None
    self.title = None
    self.minibuffer = None
    self.listbox = None
    self.head = None
    self.top = None
    self.text = None
    self.palette = [
        ('header', 'white', 'black'),
        ('text', 'dark cyan', 'black'),
        ('reveal focus', 'black', 'dark cyan', 'standout')]
    self.initGraphicalComponents()
    # gui control
    self.step = 1
    self.autoScroll = 1
  def initGraphicalComponents(self):
    self.listContent = urwid.SimpleListWalker([])
    self.listbox = urwid.ListBox(self.listContent)
    self.text = urwid.Text(u"", align='left')
    widgets = [
        self.listbox, 
        urwid.AttrMap(urwid.Filler(self.text, valign = 'top'), 'text')]
    pile = urwid.Pile(widgets);
    self.title = urwid.Text("Press any key", wrap='clip')
    head = urwid.AttrMap(self.title, 'header')
    self.minibuf = urwid.Text(": ", wrap='clip')
    bottom = urwid.AttrMap(self.minibuf, 'header')
    self.top = urwid.Frame(pile, head, bottom)
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
    if (self.autoScroll == 1):
      # Refresh focus
      self.listbox.set_focus(len(self.listContent) - 1)
    # Refresh text content
    self.text.set_text("LOL DJEOIJDEZOI %d \n fezfezfez \n zeffzefez \n jfuiezjfizeu \n fezkofzekpo" % (len(self.listContent)))
  def exitOnCr(self,  input):
    if input in ('q', 'Q'):
      raise urwid.ExitMainLoop()
  def filterInput(self, input, raw):
    return input

