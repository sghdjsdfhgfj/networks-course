from socket import *
import struct
from sys import argv

mode = argv[1]
port = int(argv[2])

k = 16
n = 4

if mode == "s":
    # server mode
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(("localhost", port))
    next_seq = {}
    with open("received.txt", "wb") as f:
        while True:
            data, addr = sock.recvfrom(1024)
            if addr not in next_seq:
                next_seq[addr] = 0
            is_ack, seq = struct.unpack("!BI", data[:5])
            if not is_ack:
                print("received message with seq =", seq)
                if next_seq[addr] == seq:
                    next_seq[addr] = (seq + 1) % k
                    f.write(data[5:])
                last_seq = (next_seq[addr] - 1) % k
                print("responding with ack", last_seq)
                sock.sendto(struct.pack("!BI",  1, last_seq), addr)

elif mode == "c":
    # client mode
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.settimeout(1)
    base = 0
    next_seq = 0
    packet_size = 4
    packet_contents = {}

    def send_packet(seq):
        print("sending packet", seq)
        packet = struct.pack("!BI", 0, seq) + packet_contents[seq]
        sock.sendto(packet, ("localhost", port))
    def print_status():
        print("Current status:")
        for i in range(k):
            print("[" if base == i else " ", end='')
            print(str(i).rjust(len(str(k)), '0'), end='')
            print("]" if (next_seq - 1) % k == i else " ", end='')
        print()

    with open("send.txt", "rb") as f:
        while next_seq + (k if next_seq < base else 0) < base + n:
            packet_contents[next_seq] = f.read(packet_size)
            send_packet(next_seq)
            next_seq = (next_seq + 1) % k
            print_status()

        while True:
            try:
                data, _ = sock.recvfrom(1024)
                is_ack, seq = struct.unpack("!BI", data[:5])
                if is_ack:
                    print("received ack", seq)
                    if len(packet_contents[seq]) == 0:
                        print("finished sending file")
                        break
                    base = (seq + 1) % k
                    print_status()
                    while next_seq + (k if next_seq < base else 0) < base + n:
                        packet_contents[next_seq] = f.read(packet_size)
                        send_packet(next_seq)
                        next_seq = (next_seq + 1) % k
                        print_status()
            except TimeoutError:
                print("timed out waiting for ack")
                for seq in range(base, next_seq):
                    send_packet(seq)
                    print_status()
