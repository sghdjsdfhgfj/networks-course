import random
import time
from socket import *
from threading import Thread

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('localhost', 8080))

disconnect_period = 15
last_heartbeats = {}

def monitor_disconnects():
    global last_heartbeats
    while True:
        now = time.time()
        for addr, last_heartbeat in list(last_heartbeats.items()):
            if now - last_heartbeat[1] > disconnect_period:
                print(f"No packets from {addr} in {disconnect_period} seconds; considered disconnected")
                del last_heartbeats[addr]
        time.sleep(1)
Thread(target=monitor_disconnects).start()

try:
    while True:
        data, addr = server_socket.recvfrom(1024)
        print("Received from", addr)
        if random.random() < 0.2:
            print("Modeling packet loss")
            continue

        message = data.decode()
        contents = " ".join(message.split()[:-2])
        number = int(message.split()[-2])
        packet_time = float(message.split()[-1])

        response = contents.upper()
        if addr not in last_heartbeats:
            information = "ok; new connection"
        else:
            last_packet, last_time = last_heartbeats[addr]
            if last_packet + 1 == number:
                information = "ok"
            else:
                information = f"lost {number - last_packet - 1} packets"
            information += f"; last packet was {packet_time - last_time:.2f}s ago"
        print("Sending response")
        server_socket.sendto(f"{response} ({information})".encode(), addr)
        last_heartbeats[addr] = (number, packet_time)
finally:
    server_socket.close()