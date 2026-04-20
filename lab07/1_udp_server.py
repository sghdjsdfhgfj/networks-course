import random
from socket import *

server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('localhost', 8080))

try:
    while True:
        data, addr = server_socket.recvfrom(1024)
        print("Received from", addr)
        if random.random() < 0.2:
            print("Modeling packet loss")
            continue
        response = data.decode().upper().encode()
        print("Sending response")
        server_socket.sendto(response, addr)
finally:
    server_socket.close()