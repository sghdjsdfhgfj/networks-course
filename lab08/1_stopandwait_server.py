import random
from socket import *

packet_loss = 0.3
file_name = "received.txt"

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('localhost', 8080))

last_ack = 1
reading = True

print(f"Saving to file {file_name}...")
with open(file_name, "w") as file:
    try:
        while reading:
            data, addr = server_socket.recvfrom(1024)
            data = data.decode()
            print(f"Received message: {data}")
            if not data.startswith("message "):
                continue
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

            if random.random() >= packet_loss:
                print(f"Sending ack {packet_no}")
                server_socket.sendto(f"ack {packet_no}".encode(), addr)
            else:
                print(f"Modeling server-side packet loss")
    finally:
        server_socket.close()