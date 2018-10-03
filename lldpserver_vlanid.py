"""
LLDP server - send lldp package with vlan-id on a vlan interface eg. eth1.51
"""
import os
import time
from scapy.all import *
import sys

def runcmd(cmd):
    x = os.popen(cmd)
    data = x.read()
    x.close()
    return data


TLV_DICTIONARY = {0x00: "End of LLDPDU",
                  0x01: "Chassis Id",
                  0x02: "Port Id",
                  0x03: "Time to Live",
                  0x04: "Port Description",
                  0x05: "System Name",
                  0x06: "System Description",
                  0x07: "System Capabilities",
                  0x08: "Management Address",
                  0x7f: "Organiation Specific"}

CHASSIS_ID_SUBTYPES = {0x00: "Reserved",
                       0x01: "Chassis component",
                       0x02: "Interface alias",
                       0x03: "Port component",
                       0x04: "MAC address",
                       0x05: "Network address",
                       0x06: "Interface name",
                       0x07: "Locally assigned"}

NETWORK_ADDRESS_TYPE = {0x01: "IPv4",
                        0x02: "IPv6"}

PORT_ID_SUBTYPES = {0x00: "Reserved",
                    0x01: "Interface alias",
                    0x02: "Port component",
                    0x03: "MAC address",
                    0x04: "Network address",
                    0x05: "Interface name",
                    0x06: "Agent circut ID",
                    0x07: "Locally assigned"}


VLAN_ID_SUBTYPES = {0x01: "Port VLAN Id"}

class Vlan_Id(Packet):
    name = "LLDP IEEE 802.1 Port VLAN Id"
    fields_desc = [BitEnumField("type", 0x7f, 7, TLV_DICTIONARY),
                   BitField("length", 6, 9),
                   X3BytesField("oui", 0x0080c2),
                   ByteEnumField("subtype", 0x01, VLAN_ID_SUBTYPES),
                   ShortField("vlan", 1001)]


class Chassis_Id(Packet):
    name = "Chassis ID"
    fields_desc = [BitEnumField("type", 0x01, 7, TLV_DICTIONARY),
                   BitField("length", 7, 9),
                   ByteEnumField("subtype", 0x04, CHASSIS_ID_SUBTYPES),
                   ConditionalField(StrLenField("reserved", "", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x00),
                   ConditionalField(StrLenField("chassisComponent", "chassis comp", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x01),
                   ConditionalField(StrLenField("interfaceAlias", "interface alias", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x02),
                   ConditionalField(StrLenField("portComponent", "port component", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x03),
                   ConditionalField(MACField("macaddr", "00:11:11:11:11:11"), lambda pkt: pkt.subtype == 0x04),
                   ConditionalField(ByteEnumField("addrType", 0x00, NETWORK_ADDRESS_TYPE), lambda pkt: pkt.subtype == 0x05),
                   ConditionalField(IPField("ipaddr", "10.10.10.10"), lambda pkt: pkt.addrType == 0x01),
                   ConditionalField(IP6Field("ip6addr", "2002::1"), lambda pkt: pkt.addrType == 0x02),
                   ConditionalField(StrLenField("interfaceName", "lo0", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x06),
                   ConditionalField(StrLenField("locallyAssigned", "yes", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x07)]


class Port_Id(Packet):
    name = "Port ID"
    fields_desc = [BitEnumField("type", 0x02, 7, TLV_DICTIONARY),
                   BitField("length", 7, 9),
                   ByteEnumField("subtype", 0x03, PORT_ID_SUBTYPES),
                   ConditionalField(StrLenField("reserved", "", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x00),
                   ConditionalField(StrLenField("interfaceAlias", "", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x01),
                   ConditionalField(ShortField("portComponent", None), lambda pkt: pkt.subtype == 0x02),
                   ConditionalField(MACField("macaddr", "00:11:11:11:11:11"), lambda pkt: pkt.subtype == 0x03),
                   ConditionalField(ByteEnumField("addrType", 0x00, NETWORK_ADDRESS_TYPE), lambda pkt: pkt.subtype == 0x04),
                   ConditionalField(IPField("ipaddr", "10.10.10.10"), lambda pkt: pkt.addrType == 0x01),
                   ConditionalField(IP6Field("ip6addr", "2002::1"), lambda pkt: pkt.addrType == 0x02),
                   ConditionalField(StrLenField("interfaceName", "lo0", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x05),
                   ConditionalField(StrLenField("agentCircutID", "id_agent", length_from=lambda x: x.length - 1), lambda pkt: pkt.subtype == 0x06),
                   ConditionalField(StrLenField("locallyAssigned", "yes", length_from=lambda x: x.length - 1),  lambda pkt: pkt.subtype == 0x07)]


class TTL(Packet):
    name = "Time To Live"
    fields_desc = [BitEnumField("type", 0x03, 7, TLV_DICTIONARY),
                   BitField("length", 0x02, 9),
                   ShortField("seconds", 32)]


class EndOfPDU(Packet):
    name = "End of LLDPDU"
    fields_desc = [BitEnumField("type", 0x00, 7, TLV_DICTIONARY),
                   BitField("length", 0x00, 9)]


def create_simple_lldp_packet(mac_addr,hostname, vlanid):
    chassis_id = Chassis_Id()
    chassis_id.subtype = 0x07
    chassis_id.locallyAssigned = hostname.strip('\n')+'z'
    print chassis_id.locallyAssigned
    chassis_id.length = len(chassis_id.locallyAssigned)+1

    port_id = Port_Id()
    port_id.subtype = 0x03
    port_id.length = 7
    port_id.macaddr = mac_addr

    vlan_id = Vlan_Id()
    vlan_id.vlan = vlanid

    ttl = TTL()
    end = EndOfPDU()

    frame = Ether()
    frame.src = mac_addr
    frame.dst = '01:80:c2:00:00:0e'
    frame.type = 0x88cc

    packet = frame / chassis_id / port_id / ttl / vlan_id / end
    return packet


def send_packet(packet, interface):
    sendp(packet, verbose=1, iface=interface)

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
            vlanid = int(intf[0].split('.')[1] if '.' in intf[0] else '1')
            packet = create_simple_lldp_packet(intf[1], hostname, vlanid)
            send_packet(packet, intf[0])
        time.sleep(30)


