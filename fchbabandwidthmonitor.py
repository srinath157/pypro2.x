"""
FC HBA Bandwidth monitor.
"""
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
ixx = {}

while True:
    for _ in ix.keys():
        with open('/sys/class/fc_host/{}/statistics/fcp_input_megabytes'.format(_), 'r') as f:
            rx = int(f.read().strip('\n'), 16) * 8 * 1024
        with open('/sys/class/fc_host/{}/statistics/fcp_output_megabytes'.format(_), 'r') as f1:
            tx = int(f1.read().strip('\n'), 16) * 8 * 1024
        ixx[_] = (rx, tx)
    ixy = dict((k, (v[0] - ix[k][0], v[1] - ix[k][1])) for k, v in ixx.items())
    ixz = dict((k, (transl(v[0], v[1]))) for k, v in ixy.items())
    # ix = dict(ixx)
    ix = ixx.copy()
    print ixz
    time.sleep(1)
