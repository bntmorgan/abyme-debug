import sys, time

timestamp = time.time()
fd = open("log", "w")

#
# 'NOTICE'
# 'WARNING'
# 'ERROR'
#
def log(s, level = 'NOTICE'):
  fd.write("[%d]%s: %s\n" % (time.time() - timestamp, level, s))

def logClose():
  fd.close()
