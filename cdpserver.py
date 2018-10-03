#!/usr/local/bin/python
"""
CDP Server - Sends CDP packets from the linux server
"""
import os
import time
from scapy.all import *


def runcmd(cmd):
    x = os.popen(cmd)
    data = x.read()
    x.close()
    return data


def __CDPcopy(code, v):
    x = bytearray(b'\0' * (len(v) + 4))
    x[0] = 0
    x[1] = struct.pack( 'B', code)
    x[2] = 0
    x[3] = struct.pack( 'B', len(v) + 4 )
    x[4:] = v
    return x


def CDPpak(box, iface, platform, description):
    x0 = bytearray((2, 240, 0, 0))
    if (len(box) + len(iface) + len(description) + len(platform)) % 2 == 1 : description += ' '
    x1 = __CDPcopy(1, box)
    x2 = __CDPcopy(3, iface)
    x3 = __CDPcopy(4, b'\0\0\0\x10')
    x4 = __CDPcopy(5, description)
    x5 = __CDPcopy(6, platform)
    x = x0 + x1 + x2 + x3 + x4 + x5
    x = str(x)
    ck = checksum(x)
    p = x[:2] + struct.pack( "!H", ck) + x[4 :]
    pak = Ether(dst='01:00:0c:cc:cc:cc', src='00:12:34:56:78:90', type=len(p) + 8)
    pak = pak / LLC(dsap=0xaa , ssap=0xaa , ctrl=3 )
    pak = pak / SNAP(OUI=12 , code=0x2000 )
    pak = pak / Raw(p)
    return pak

def intf_mac_set(os):
    if os == 'rhel6':
        x = runcmd('ifconfig | grep -E ^eth').splitlines()
        x = [_.split() for _ in x if x]
        intflist = set()
        [intflist.add((_[0],_[4])) for _ in x]
        return intflist
    if os == 'rhel7':
        x = [_.split(':')[0] for _ in runcmd('ifconfig | grep -E ^enp').splitlines()]
        y = [runcmd('ifconfig %s | grep -i ether' % _).strip().split()[1] for _ in x]
        return zip(x,y)


if __name__ == '__main__':
    hostname = runcmd('hostname')
    intflist = intf_mac_set('rhel7')
    while True:
        for intf in intflist:
            print intf[0], intf[1]
            cdpp = CDPpak(hostname, intf[0], "ITGEN-srinath", 'Cisco ITGEN test platform')
            sendp(cdpp, iface=intf[0], verbose= False, count= 1)
            print 'sent cdp pkt on interface:{0}'.format(intf[0])
        print 'sleeping for 60 sec'
        time.sleep( 60)

