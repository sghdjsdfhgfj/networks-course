import time
from socket import *
import struct
from sys import argv
import os

def calculate_checksum(data):
    checksum = 0
    if len(data) % 2 != 0:
        data += b"\x00"
    for i in range(0, len(data), 2):
        checksum += (data[i] << 8) + data[i + 1]
    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum += checksum >> 16
    return (~checksum) & 0xffff


icmp_type = 8
icmp_code = 0
icmp_id = os.getpid() % 65536
icmp_sequence = 1

host = gethostbyname(argv[1])
packets = int(argv[2]) if len(argv) > 2 else 3
sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
sock.settimeout(1)
for ttl in range(1, 64):
    sock.setsockopt(IPPROTO_IP, IP_TTL, struct.pack("I", ttl))

    rtts = []
    recv_addr = None

    success = False
    for i in range(packets):
        icmp_packet = struct.pack("!BBHHH", icmp_type, icmp_code, 0, icmp_id, icmp_sequence)
        checksum = calculate_checksum(icmp_packet)
        icmp_packet = icmp_packet[:2] + struct.pack("!H", checksum) + icmp_packet[4:]

        current_time = time.time()
        sock.sendto(icmp_packet, (host, 0))
        icmp_sequence += 1
        try:
            data, addr = sock.recvfrom(1024)
            if calculate_checksum(data) or calculate_checksum(data[20:]):
                print("received malformed packet")
            else:
                recv_type, recv_code = struct.unpack("!BB", data[20:22])
                if recv_type == 0 and recv_code == 0:
                    success = True
                if recv_type in (0, 11) and recv_code == 0:
                    rtts.append((time.time() - current_time) * 1000)
                    recv_addr = addr[0]
                else:
                    print(f"received error: ({recv_type}, {recv_code})")
        except TimeoutError:
            pass

    if recv_addr is None:
        print(f"hop {ttl}:\t0/{packets} responses\taddr = ??.??.??.??\thostname = ??")
    else:
        try:
            hostname = gethostbyaddr(recv_addr)[0]
        except herror:
            hostname = "??"
        rtts.sort()
        print(f"hop {ttl}:\t{len(rtts)}/{packets} responses\taddr = {recv_addr}\thostname = {hostname}")
        print(f"rtts:\t{"\t".join("{:.1f}ms".format(x) for x in rtts)}")
    print()
    if success:
        break
