import time
import sys
import struct
import socket
import random

try:
    out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()
 
host = 'localhost'
cr3_port = 5000
md5hv_port = 5001
md5fun_port = 5002

count = 0 
while 1:
  try:
    msg = ""
    for i in range(16):
      msg = msg + struct.pack('q', random.random() * 0x1000000000000000)
    out.sendto(msg, (host, cr3_port))

    if count % 50 == 0:
      rnd = random.random()
      if rnd > 0.75:
        msg = "123456789abcdefg"
      else:
        msg = "gfedcbs987654321"
      out.sendto(msg, (host, md5hv_port))

    if count % 50 == 5:
      rnd = random.random()
      if rnd > 0.75:
        msg = "123456789abcdefg"
      else:
        msg = "gfedcbs987654321"
      out.sendto(msg, (host, md5fun_port))
  except socket.error, msg:
    print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
  time.sleep(0.1)
  count = count + 1
