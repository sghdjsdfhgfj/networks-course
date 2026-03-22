import multiprocessing
import os
from datetime import datetime
from http import HTTPStatus
from socket import *
from sys import argv
import pathlib
from textwrap import dedent

root = pathlib.Path(os.getcwd()).absolute()
format_string = "%a, %d %b %Y %H:%M:%S %z"
server_name = "hw3/1.0"

def process_request(conn):
    request = bytes()
    while True:
        try:
            data = conn.recv(1024, MSG_DONTWAIT)
        except IOError:
            break
        request += data
    data = request.decode().replace('\r\n', '\n').split('\n\n')[0]
    header_lines = data.split('\n')
    method, path, protocol = header_lines[0].split(' ')
    if method == 'GET':
        file_path = root / path[1:]
        print('requesting path', file_path)
        if not file_path.exists():
            status_code = HTTPStatus.NOT_FOUND
            content_length = 0
            last_modified = datetime.now()
            file = None
        else:
            status_code = HTTPStatus.OK
            stat = file_path.stat()
            content_length = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            file = file_path.open('rb')
    else:
        status_code = HTTPStatus.METHOD_NOT_ALLOWED
        content_length = 0
        last_modified = datetime.now()
        file = None

    response = dedent(f"""
        {protocol} {status_code.value} {status_code.phrase}
        Date: {datetime.now().strftime(format_string)}
        Server: {server_name}
        Last-Modified: {last_modified.strftime(format_string)}
        Accept-Ranges: bytes
        Content-Length: {content_length}
        Connection: close

    """).lstrip().replace('\n', '\r\n').encode()
    conn.sendall(response)
    if file is not None:
        while True:
            data = file.read(2048)
            if not data:
                break
            conn.sendall(data)
    conn.close()
    print('finished processing request')

thread_pool = multiprocessing.Pool(processes=int(argv[2]))
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', int(argv[1])))
server_socket.listen(1)
try:
    while True:
        conn, addr = server_socket.accept()
        thread_pool.apply_async(process_request, args=(conn,))
finally:
    thread_pool.close()
    server_socket.close()