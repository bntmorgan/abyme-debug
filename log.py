import sys, time

timestamp = time.time()
fd = open("log", "w")
fdinfo = {}

#
# 'NOTICE'
# 'WARNING'
# 'ERROR'
#
def log(s, level = 'NOTICE'):
  fd.write("[%06d]%-8s: %s\n" % (time.time() - timestamp, level, s))
  fd.flush()

def info(l, s):
  try:
    fdi = fdinfo[l]
  except:
    fdinfo[l] = open("info_%d" % (l), "w")
    fdi = fdinfo[l]
  fdi.write(s)
  fdi.flush()

def logClose():
  fd.close()
