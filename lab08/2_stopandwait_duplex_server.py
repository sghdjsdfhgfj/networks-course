import random
import threading
import time
from socket import *

timeout = 1
packet_loss = 0.3
packet_size = 16
file_name = "received.txt"
file_to_send = "transfer_test.txt"

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('localhost', 8080))

last_ack = 1
reading = True

files = {}
contents = {}
message_no = {}

def send(message, addr):
    if random.random() >= packet_loss:
        print(f"Sending message: {message}")
        server_socket.sendto(message.encode(), addr)
    else:
        print(f"Modeling server-side packet loss for message {message}")

def handle_timeout(addr, cur_message_no):
    global message_no
    while True:
        time.sleep(timeout)
        if addr not in message_no:
            break
        if cur_message_no == message_no[addr]:
            print("Timed out waiting for acknowledgement")
            send(f"message {cur_message_no % 2} {contents[addr]}", addr)

print(f"Saving to file {file_name}...")
with open(file_name, "w") as file:
    while True:
        data, addr = server_socket.recvfrom(1024)
        if addr not in files:
            print(f"New connection from {addr}. Starting to send file...")
            files[addr] = open(file_to_send, "r")
            contents[addr] = files[addr].read(8)
            message_no[addr] = 0
            send(f"message {message_no[addr]} {contents[addr]}", addr)
            threading.Thread(target=handle_timeout, args=(addr, message_no[addr])).start()

        data = data.decode()
        print(f"Received message: {data}")
        if data.startswith("message "):
            packet_no = int(data.split(' ')[1])
            if packet_no != last_ack:
                last_ack = packet_no
                packet_contents = data.split(' ', 2)[2]
                if len(packet_contents) == 0:
                    print("Received empty packet; considering EOF")
                    reading = False
                file.write(packet_contents)
            else:
                print("Duplicate message; not writing to file")
            send(f"ack {packet_no}", addr)
        elif data.startswith("ack "):
            packet_no = int(data.split(' ')[1])
            if addr not in message_no:
                print(f"ACK from an unknown address: {addr}")
                continue
            if packet_no == message_no[addr] % 2:
                message_no[addr] += 1
                if len(contents[addr]) == 0:
                    print("Successfully sent file!")
                    files[addr].close()
                else:
                    contents[addr] = files[addr].read(packet_size)
                    send(f"message {message_no[addr] % 2} {contents[addr]}", addr)
                    threading.Thread(target=handle_timeout, args=(addr, message_no[addr])).start()