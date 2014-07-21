import sys, time

timestamp = time.time()
fd = open("log", "w")

#
# 'NOTICE'
# 'WARNING'
# 'ERROR'
#
def log(s, level = 'NOTICE'):
  fd.write("[%06d]%-8s: %s\n" % (time.time() - timestamp, level, s))
  fd.flush()

def logClose():
  fd.close()
