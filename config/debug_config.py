#!/usr/bin/env python

#import itertools, sys, curses, os, pprint
import sys, os
from config import Config, Menu, Ordict

class DebugConfig(Config):
  def __init__(self, fname):
    Config.__init__(self, fname)

##
## main
##
if len(sys.argv) != 2:
    print "usage: %s <config_file_name>" % sys.argv[0]
    sys.exit(1)

Menu(DebugConfig(sys.argv[1])).interact()
