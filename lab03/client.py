import sys
from socket import *
from sys import argv
from textwrap import dedent

server_host, server_port, filename = argv[1:]
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_host, int(server_port)))

request = dedent(f"""
    GET /{filename} HTTP/1.1
    Host: {server_host}:{server_port}
    User-Agent: hw3/1.0
    Connection: close

""").lstrip().encode()
client_socket.send(request)

headers_bytes = client_socket.recv(1024)
headers = headers_bytes.decode()

status = headers.split('\r\n')[0].split(' ', 1)[1]
if status != '200 OK':
    print("Server returned status", status)
else:
    headers_lines = headers.split('\r\n')[1:]
    content_length = 0
    for line in headers_lines:
        if line.startswith('Content-Length'):
            content_length = int(line.split(': ')[1])
    received = 0
    while received < content_length:
        data = client_socket.recv(1024)
        if not data:
            break
        received += len(data)
        sys.stdout.buffer.write(data)
        sys.stdout.flush()
    print()
client_socket.close()