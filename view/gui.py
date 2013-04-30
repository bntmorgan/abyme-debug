from struct import *

import urwid

class Gui():
  def __init__(self):
    self.network = None
    self.listContent = None
    self.title = None
    self.minibuffer = None
    self.listbox = None
    self.head = None
    self.top = None
    self.palette = [
        ('header', 'white', 'black'),
        ('text', 'dark cyan', 'black'),
        ('reveal focus', 'black', 'dark cyan', 'standout')]
    self.initGraphicalComponents()
  def initGraphicalComponents(self):
    self.listContent = urwid.SimpleListWalker([])
    self.listbox = urwid.ListBox(self.listContent)
    text = urwid.Text(u"", align='left')
    widgets = [
        self.listbox, 
        urwid.AttrMap(urwid.Filler(text, valign = 'top'), 'text')]
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
  def notifyMessage(message):
    if (eth_protocol == 8):
      t = urwid.Text('Destination MAC : ' + eth_addr(packet[0:6]) + ' Source MAC : ' + eth_addr(packet[6:12]) + ' Protocol : ' + str(eth_protocol))
      content.append(urwid.AttrMap(t, None, 'reveal focus'))
      #if (scroll == 1):
      listbox.set_focus(len(content) - 1)
  def exitOnCr(self,  input):
    if input in ('q', 'Q'):
      raise urwid.ExitMainLoop()
  def filterInput(self, input, raw):
    return input

