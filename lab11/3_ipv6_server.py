from socket import *
from threading import Thread

server = socket(AF_INET6, SOCK_STREAM)
server.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 1)
server.bind(('::1', 8080))
server.listen(1)

def main(conn):
    while True:
        try:
            data = conn.recv(1024)
        except IOError:
            break
        conn.send(data.decode().upper().encode())

while True:
    conn, addr = server.accept()
    print("Accepted connection from", addr)
    Thread(target=main, args=(conn,)).start()