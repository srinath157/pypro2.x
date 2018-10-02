"""
Ethernet interface Bandwidth monitor.
argv = ['eth0', 'eth4']
"""
import re
import time
import sys


def transl(rx_rate, tx_rate):
    if rx_rate < 1024:
        rx_rate = '%.2f Kbps' % rx_rate
    elif 1024 < rx_rate < 1048576:
        rx_rate = '%.2f Mbps' % (rx_rate / 1024)
    elif rx_rate > 1048576:
        rx_rate = '%.2f Gbps' % (rx_rate / 1048576)
    if tx_rate < 1024:
        tx_rate = '%.2f Kbps' % tx_rate
    elif 1024 < tx_rate < 1048576:
        tx_rate = '%.2f Mbps' % (tx_rate / 1024)
    elif tx_rate > 1048576:
        tx_rate = '%.2f Gbps' % (tx_rate / 1048576)
    return rx_rate, tx_rate


argv = sys.argv[1].split(',')
print argv, type(argv)

ix = dict((_, (0, 0)) for _ in argv)

while True:
    with open('/proc/net/dev', 'r') as f: data = f.read().splitlines()[2:]
    i = [re.split(r'[: ]+', _.strip()) for _ in data]
    ixx = dict((_[0], (int(_[1]) * 8.0 / 1024, int(_[9]) * 8.0 / 1024)) for _ in i if _[0] in ix)
    ixy = dict((k, (v[0] - ix[k][0], v[1] - ix[k][1])) for k, v in ixx.items())
    ixz = dict((k, (transl(v[0], v[1]))) for k, v in ixy.items())
    ix = ixx
    print ixz
    time.sleep(1)
