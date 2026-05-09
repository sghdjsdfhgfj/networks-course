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


ttl = 64
icmp_type = 8
icmp_code = 0
icmp_id = os.getpid() % 65536
icmp_sequence = 1

host = gethostbyname(argv[1])
port = argv[2] if len(argv) > 2 else 0
sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
sock.settimeout(1)
sock.setsockopt(IPPROTO_IP, IP_TTL, struct.pack("I", ttl))

rtts = []
losses = 0

while True:
    print(f"Ping {icmp_sequence}: ", end='')

    current_time = round(time.time() * 1000000)
    icmp_packet = struct.pack("!BBHHHQ", icmp_type, icmp_code, 0, icmp_id, icmp_sequence, current_time)
    checksum = calculate_checksum(icmp_packet)
    icmp_packet = icmp_packet[:2] + struct.pack("!H", checksum) + icmp_packet[4:]

    sock.sendto(icmp_packet, (host, port))
    try:
        data, addr = sock.recvfrom(1024)
        #print(data)
        if calculate_checksum(data) or calculate_checksum(data[20:]):
            print("received malformed packet")
            losses += 1
        else:
            recv_type, recv_code, _, _, _, recv_time = struct.unpack("!BBHHHQ", data[20:])
            rtt = time.time() - recv_time / 1000000
            print(f"success rtt = {round(rtt * 1000, 2)} ms")
            rtts.append(rtt)
    except TimeoutError:
        print("timed out")
        losses += 1

    if len(rtts) > 0:
        min_rtt = round(min(rtts) * 1000)
        max_rtt = round(max(rtts) * 1000)
        avg_rtt = round(sum(rtts) / len(rtts) * 1000)
        loss_pct = round(losses / icmp_sequence * 100)
        print(f"""Ping statistics:
    Packets: Sent = {icmp_sequence}, Received = {icmp_sequence - losses}, Lost = {losses} ({loss_pct}% loss),
Approximate round trip times in milli-seconds:
    Minimum = {min_rtt}ms, Maximum = {max_rtt}ms, Average = {avg_rtt}ms""")
    print()
    time.sleep(1)
    icmp_sequence += 1