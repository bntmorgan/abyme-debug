from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import matplotlib
import time
import random
import os
import stat
import struct
import socket

# Le dialogue entre la gui et les debuggeur se fait via udp.
def open_udp(port):
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.bind(("", port))
  s.setblocking(0)
  return s

def read_udp(s):
  try:
    data, address = s.recvfrom(4096)
  except socket.error:
    return ""
  else: 
    return data

# Pour les cr3, des plages de valeurs ne sont pas utilisees (ce n'est pas jolie).
# Elles correspondent a priori a l'espace memoire occupe par du code ou des donnees et non des
# pages pointees par des cr3. On essaye de les minimiser (au lieu de demander a matplotlib de
# tronquer des morceaux de l'axe y, on coupe la donnees elle meme). Ces donnees permettent
# d'identifier les coupes.
# limits correspond a priori au zones ou les donnees sont agglomerees.
# minmax correspond, pour chacune de ces zones, au min et au max.
limits = [[0, 0.08e10], [0.08e10, 0.25e10],  [0.25e10, 0.5e10], [1e10, 2e10]]
minmax = [[-1, -1], [-1, -1], [-1, -1],   [-1, -1]]
#limits = [[0, 0.4e10], [1.68e10, 2.0e10]]
#minmax = [[0, 0.4e10], [1.68e10, 2.0e10]]

# Nombre de points dans les figures et points.
NBCR3 = 10000
NBMD5HV = 100
NBMD5FUN = 100
xcr3 = range(NBCR3)
ycr3 = [0] * NBCR3
xmd5hv = range(NBMD5HV)
ymd5hv = [0] * NBMD5HV
xmd5fun = range(NBMD5FUN)
ymd5fun = [0] * NBMD5FUN

# Donnees en cours de traitement.
cr3_pending = ""
md5hv_pending = ""
md5fun_pending = ""
md5fun_ref = None


matplotlib.rcParams['toolbar'] = 'None'

fig = plt.figure()

plt.subplots_adjust(left=0.04, right=0.98, top=0.95, bottom=0.06, wspace=0.1)

ax = plt.subplot2grid((2,2), (0,0), rowspan=2)
cr3, = plt.plot(xcr3, ycr3, 'ro', markersize=10.0)
plt.title('Running process', fontsize=18)
plt.xlabel('Scheduling', fontsize=14)
plt.ylabel('Process identifier', fontsize=14)
frame = plt.gca()
frame.set_ylim([0, 0.16e10])
#frame.set_ylim([0, 2.0e10])

frame.axes.get_xaxis().set_ticks([])
frame.axes.get_yaxis().set_ticks([])

plt.subplot2grid((2,2), (0,1))
md5fun, = plt.plot(xmd5fun, ymd5fun, color="g", linewidth=4.0)
plt.title('Module integrity', fontsize=18)
plt.xlabel('Time', fontsize=14)
plt.ylabel('Module MD5', fontsize=14)
frame = plt.gca()
frame.set_ylim([-1.5, 1.5])
frame.axes.get_xaxis().set_ticks([])
frame.axes.get_yaxis().set_ticks([])
frame_cr3 = frame

plt.subplot2grid((2,2), (1,1))
md5hv, = plt.plot(xmd5hv, ymd5hv, color="g", linewidth=4.0)
plt.title('Hypervisor integrity', fontsize=18)
plt.xlabel('Time', fontsize=14)
plt.ylabel('Hypervisor MD5', fontsize=14)
frame = plt.gca()
frame.set_ylim([-1.5, 1.5])
frame.axes.get_xaxis().set_ticks([])
frame.axes.get_yaxis().set_ticks([])

def init():
  global cr3
  global md5hv
  global md5fun
  cr3.set_data([],[])
  md5hv.set_data([],[])
  md5fun.set_data([],[])
  return cr3, md5hv, md5fun

def animate(i):
    global ycr3
    global xcr3
    global ymd5hv
    global xmd5hv
    global ymd5fun
    global xmd5fun
    global md5hv_in
    global md5hv_ref
    global md5fun_ref
    global cr3_pending
    global md5hv_pending
    global md5fun_pending
    #global limits
    #global minmax
    global frame_cr3

    cr3_pending = cr3_pending + read_udp(cr3_in)
    if (len(cr3_pending) == 0):
      cr3.set_data(xcr3, ycr3)
    else:
      while len(cr3_pending) >= 8:
        value = struct.unpack('q', cr3_pending[:8])[0]
        value = value & 0xfffffffffffff000
        # mise a jour des bornes
        for i in range(len(limits)):
          if value >= limits[i][0] and value <= limits[i][1]:
            if minmax[i][0] == -1:
              minmax[i][0] = value
              minmax[i][1] = value
            minmax[i][0] = min(minmax[i][0], value)
            minmax[i][1] = max(minmax[i][1], value)
            break
        # correction de la valeur
        rectification = 0
        for i in range(len(limits) - 1):
          if value < limits[i][1]:
            break
          rectification = rectification + minmax[i + 1][0] - minmax[i][1]
        value = value - rectification
        ycr3 = ycr3[1:] + [value]
        cr3_pending = cr3_pending[8:] + read_udp(cr3_in)
      cr3.set_data(xcr3, ycr3)
      # print(minmax)
      # print(limits)

    md5hv_pending = md5hv_pending + read_udp(md5hv_in)
    if (len(md5hv_pending) < 1):
      if i == 5:
        ymd5hv = ymd5hv[1:] + [0]
        md5hv.set_data(xmd5hv, ymd5hv)
    else:
      if len(md5hv_pending) >= 1:
        while len(md5hv_pending) >= 1:
          value = struct.unpack('b', md5hv_pending[:1])[0]
          if value == 1:
            ymd5hv = ymd5hv[1:] + [1]
          else:
            ymd5hv = ymd5hv[1:] + [-1]
          md5hv_pending = md5hv_pending[1:] + read_udp(md5hv_in)
        md5hv.set_data(xmd5hv, ymd5hv)
      elif i == 5:
        ymd5hv = ymd5hv[1:] + [0]
        md5hv.set_data(xmd5hv, ymd5hv)

    # reference value
    if md5fun_ref == None:
      md5fun_pending = md5fun_pending + read_udp(md5fun_in)
      if (len(md5fun_pending) == 0):
        if i == 5:
          md5fun.set_data(xmd5fun, ymd5fun)
          ymd5fun = ymd5fun[1:] + [0]
      else:
        while len(md5fun_pending) < 16:
          md5fun_pending = md5fun_pending + read_udp(md5fun_in)
        md5fun_ref = md5fun_pending[:16]
        md5fun_pending = md5fun_pending[16:]
    else:
      md5fun_pending = md5fun_pending + read_udp(md5fun_in)
      if (len(md5fun_pending) < 16):
        if i == 5:
          md5fun.set_data(xmd5fun, ymd5fun)
          ymd5fun = ymd5fun[1:] + [0]
      else:
        if len(md5fun_pending) >= 16:
          while len(md5fun_pending) >= 16:
            if md5fun_pending[:16] == md5fun_ref:
              ymd5fun = ymd5fun[1:] + [1]
            else:
              ymd5fun = ymd5fun[1:] + [-1]
            md5fun_pending = md5fun_pending[16:] + read_udp(md5fun_in)
          md5fun.set_data(xmd5fun, ymd5fun)
        elif i == 5:
          ymd5fun = ymd5fun[1:] + [0]
          md5fun.set_data(xmd5fun, ymd5fun)

    return cr3, md5hv, md5fun

cr3_in = open_udp(5000)
md5hv_in = open_udp(5001)
md5fun_in = open_udp(5002)

#while len(md5hv_pending) < 16:
#  md5hv_pending = md5hv_pending + read_udp(md5hv_in)
#md5hv_ref = md5hv_pending[:16]
#md5hv_pending = md5hv_pending[16:]


ani = animation.FuncAnimation(fig, animate, init_func=init, frames=10, blit=True, interval=1, repeat=True)

plt.show()

cr3_in.close()
md5hv_in.close()
md5fun_in.close()
