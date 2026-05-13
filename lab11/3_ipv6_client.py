from socket import *

sock = socket(AF_INET6, SOCK_STREAM)
sock.connect(('::1', 8080))
while True:
    data = input('> ')
    sock.send(data.encode())
    print(sock.recv(1024).decode())