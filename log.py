import sys, time

timestamp = time.time()
fd = None
prefix = 'none'
fdinfo = {}

def setup(pf):
  global fd
  global prefix
  prefix = pf
  fd = open("log_%s" % (prefix), "w")

#
# 'NOTICE'
# 'WARNING'
# 'ERROR'
#
def log(s, level = 'NOTICE'):
  fd.write("[%06d]%-8s: %s\n" % (time.time() - timestamp, level, s))
  fd.flush()

def info(l, s):
  global fdinfo
  try:
    fdi = fdinfo[l]
  except:
    fdinfo[l] = open("info_%s_%d" % (prefix, l), "w")
    fdi = fdinfo[l]
  fdi.write(s)
  fdi.flush()

def logClose():
  fd.close()
