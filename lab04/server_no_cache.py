import multiprocessing
from datetime import datetime
from http import HTTPStatus
from socket import *
from sys import argv
from textwrap import dedent

format_string = "%a, %d %b %Y %H:%M:%S %z"
server_name = "hw4/1.0"

def get_page(method, path, body):
    if '/' not in path:
        host = path
        path = ''
    else:
        host, path = path.split('/', 1)
    client_socket = socket(AF_INET, SOCK_STREAM)
    try:
        client_socket.connect((host, 80))
    except Exception as e:
        return 500, str(e).encode()

    request = (dedent(f"""
        {method} /{path} HTTP/1.1
        Host: {host}
        Accept: */*
        User-Agent: {server_name}
        Content-Length: {len(body)}
        Connection: keep-alive
        
        """) + body).lstrip().encode()
    client_socket.send(request)

    data = client_socket.recv(4096)
    headers = data.decode()
    if len(headers) == 0:
        return 400, "server returned empty response".encode()

    status = headers.split('\r\n')[0].split(' ', 1)[1]
    status_code = int(status.split(' ')[0])
    data = data.split('\r\n\r\n'.encode(), 1)[1]
    if status_code >= 400:
        client_socket.close()
        return status_code, f"Server returned status {status}".encode()
    else:
        headers_lines = headers.split('\r\n')[1:]
        content_length = 0
        for line in headers_lines:
            if line.startswith('Content-Length'):
                content_length = int(line.split(': ')[1])
        while len(data) < content_length:
            new_data = client_socket.recv(1024)
            #if not data:
            #    break
            data += new_data
        client_socket.close()
        return status_code, data

def process_request(conn):
    request = bytes()
    while True:
        try:
            data = conn.recv(1024, MSG_DONTWAIT)
        except IOError:
            break
        request += data
    header, body = request.decode().replace('\r\n', '\n').split('\n\n', 1)
    method, path, protocol = header.split('\n')[0].split(' ')
    if method == 'GET' or method == 'POST':
        file_path = path[1:]
        print(f'request {method} {file_path}')
        status_code, body = get_page(method, file_path, body)
        status_code = HTTPStatus(status_code)
        print(f'{file_path} returned status code {status_code}')
    else:
        status_code = HTTPStatus.METHOD_NOT_ALLOWED
        body = bytes()

    content_length = len(body)
    response = dedent(f"""
        {protocol} {status_code.value} {status_code.phrase}
        Date: {datetime.now().strftime(format_string)}
        Server: {server_name}
        Accept-Ranges: bytes
        Content-Length: {content_length}
        Connection: close

    """).lstrip().replace('\n', '\r\n').encode() + body
    conn.send(response)
    conn.close()

server_port = int(argv[1])
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', server_port))
server_socket.listen(1)
try:
    while True:
        conn, addr = server_socket.accept()
        thread = multiprocessing.Process(target=process_request, args=(conn,))
        thread.start()

except KeyboardInterrupt:
    server_socket.close()