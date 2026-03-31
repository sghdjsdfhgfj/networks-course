import time
from datetime import datetime
import json
from http import HTTPStatus
from socket import *
from sys import argv
from textwrap import dedent

format_string = "%a, %d %b %Y %H:%M:%S %z"
server_name = "hw4/1.0"
cache_name = "cache.json"

def get_page(method, path, body, timestamp = None):
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

    if timestamp is not None:
        if_modified_since = f"If-Modified-Since: {datetime.fromtimestamp(timestamp).strftime(format_string)}\n"
    else:
        if_modified_since = ""
    request = (dedent(f"""
        {method} /{path} HTTP/1.1
        Host: {host}
        Accept: text/html
        User-Agent: {server_name}
        Content-Length: {len(body)}
        Connection: keep-alive
        {if_modified_since}
        """) + body).lstrip().encode()
    client_socket.send(request)

    data = client_socket.recv(4096)
    headers = data.decode().split('\r\n\r\n')[0]
    if len(headers) == 0:
        return 400, "server returned empty response".encode()

    header_lines = {}
    for x in headers.split('\r\n')[1:]:
        k, v = x.split(':', 1)
        header_lines[k] = v
    status = headers.split('\r\n')[0].split(' ', 1)[1]
    status_code = int(status.split(' ')[0])
    data = data.split('\r\n\r\n'.encode(), 1)[1]
    if timestamp is not None and status_code == 304:
        return 304, bytes()
    if status_code >= 400:
        client_socket.close()
        return status_code, f"Server returned status {status}".encode()
    else:
        content_length = int(header_lines.get('Content-Length', 0))
        while len(data) < content_length:
            new_data = client_socket.recv(1024)
            #if not data:
            #    break
            data += new_data
        client_socket.close()
        return status_code, data

def save_cache(method, path, body, status_code, response_body):
    with open(cache_name) as cache_file:
        cache = json.load(cache_file)
    if method == 'GET':
        cache.setdefault(path, {})
        cache[path][body] = (time.time(), status_code, response_body.decode())
        with open(cache_name, 'w') as cache_file:
            json.dump(cache, cache_file)

def process_request(conn):
    with open(cache_name) as cache_file:
        cache = json.load(cache_file)
    request = bytes()
    while True:
        try:
            data = conn.recv(1024, MSG_DONTWAIT)
        except IOError:
            break
        request += data
    header, body = request.decode().replace('\r\n', '\n').split('\n\n', 1)
    method, path, protocol = header.split('\n')[0].split(' ')
    path = path[1:]
    if method == 'GET' and path in cache and body in cache[path]:
        last_modified, status_code, response_body = cache[path][body]
        new_status_code, new_response_body = get_page(method, path, body, timestamp = last_modified)
        if new_status_code != 304:
            print(f'request {method} {path} found in cache but modified since, replacing')
            status_code = new_status_code
            response_body = new_response_body
            save_cache(method, path, body, new_status_code, new_response_body)
        else:
            print(f'request {method} {path} found in cache')
            response_body = response_body.encode()
        status_code = HTTPStatus(status_code)
    elif method == 'GET' or method == 'POST':
        print(f'request {method} {path}')
        status_code, response_body = get_page(method, path, body)
        save_cache(method, path, body, status_code, response_body)
        status_code = HTTPStatus(status_code)
        print(f'{path} returned status code {status_code}')
    else:
        status_code = HTTPStatus.METHOD_NOT_ALLOWED
        response_body = bytes()

    content_length = len(response_body)
    response = dedent(f"""
        {protocol} {status_code.value} {status_code.phrase}
        Date: {datetime.now().strftime(format_string)}
        Server: {server_name}
        Accept-Ranges: bytes
        Content-Length: {content_length}
        Connection: close

    """).lstrip().replace('\n', '\r\n').encode() + response_body
    conn.send(response)
    conn.close()

server_port = int(argv[1])
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', server_port))
server_socket.listen(1)
try:
    while True:
        conn, addr = server_socket.accept()
        try:
            process_request(conn)
        finally:
            conn.close()
finally:
    server_socket.close()