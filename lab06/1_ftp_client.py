import os
from socket import *
from textwrap import dedent

debug = False

def _send(ftp_socket, c):
    if debug:
        print('>', c.decode().strip())
    ftp_socket.send(c)

def _recv(ftp_socket):
    res = ftp_socket.recv(1024).strip().decode()
    if debug:
        print('<', res)
    return res

def _status(ftp_socket):
    return int(_recv(ftp_socket)[:3])

def _success(ftp_socket):
    return 200 <= _status(ftp_socket) < 300

def get_data_connection(ftp_socket, recv_socket, cmd):
    _send(ftp_socket, b'PORT 127,0,0,1,31,144\r\n')
    status_code = _status(ftp_socket)
    if status_code == 500:
        _send(ftp_socket, b'PASV\r\n')
        response = _recv(ftp_socket)
        _send(ftp_socket, cmd)
        ip0, ip1, ip2, ip3, port0, port1  = map(int, response.split('(')[1].split(')')[0].split(','))
        data_socket = socket(AF_INET, SOCK_STREAM)
        data_socket.connect((f"{ip0}.{ip1}.{ip2}.{ip3}", port0 * 256 + port1))
        status_code = _status(ftp_socket)
        if status_code != 150:
            return None
        return data_socket
    else:
        _send(ftp_socket, cmd)
        status_code = _status(ftp_socket)
        if status_code != 150:
            return None
        return recv_socket.accept()[0]


def list_files(ftp_socket, recv_socket, indent=0):
    conn = get_data_connection(ftp_socket, recv_socket, b'NLST\r\n')
    if conn is None:
        return
    files = []
    while True:
        data = conn.recv(1024)
        if not data:
            break
        files.append(data)
    conn.close()
    _recv(ftp_socket)

    for file in files:
        print('\t' * indent + file.decode().strip())
        _send(ftp_socket, b'CWD ' + file + b'\r\n')
        res = _recv(ftp_socket)
        if 200 <= int(res.split(' ')[0]) < 300:
            list_files(ftp_socket, recv_socket, indent + 1)
            _send(ftp_socket, b'CDUP\r\n')
            _recv(ftp_socket)


def get_file(ftp_socket, recv_socket, ftp_path):
    local_file = ftp_path.split('/')[-1]
    _send(ftp_socket, b'TYPE I\r\n')
    _recv(ftp_socket)
    conn = get_data_connection(ftp_socket, recv_socket, b'RETR ' + ftp_path.encode() + b'\r\n')
    if conn is None:
        return
    with open(local_file, 'wb') as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
    conn.close()
    _recv(ftp_socket)
    print('Saved to', local_file)


def upload_file(ftp_socket, recv_socket, local_path, ftp_path):
    if not os.path.exists(local_path) or not os.path.isfile(local_path):
        print('File not found')
    components = ftp_path.split('/')
    for i in range(len(components)):
        p = '/'.join(components[:i+1])
        _send(ftp_socket, b'MKD ' + p.encode() + b'\r\n')
        _recv(ftp_socket)

    ftp_path = os.path.join(ftp_path, os.path.basename(local_path))
    ftp_path = ftp_path.replace('\\', '/')
    print('Uploading to', ftp_path, '...')

    conn = get_data_connection(ftp_socket, recv_socket, b'STOR ' + ftp_path.encode() + b'\r\n')
    if conn is None:
        return
    with open(local_path, 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            conn.send(data)
    conn.close()
    _recv(ftp_socket)


recv_socket = socket(AF_INET, SOCK_STREAM)
recv_socket.bind(('127.0.0.1', 8080))
recv_socket.listen(1)

ftp_socket = socket(AF_INET, SOCK_STREAM)
ftp_socket.connect(("127.0.0.1", 21))
_recv(ftp_socket)
_send(ftp_socket, b'USER TestUser\r\n')
_recv(ftp_socket)
_send(ftp_socket, b'PASS\r\n')
_recv(ftp_socket)

try:
    while True:
        command = input('>> ').strip().lower()
        match command:
            case "list":
                list_files(ftp_socket, recv_socket)
            case "get":
                ftp_path = input('Enter path to FTP file: ')
                get_file(ftp_socket, recv_socket, ftp_path)
            case "upload":
                local_path = input('Enter path to file to upload: ')
                ftp_path = input('Enter folder to place the file in: ')
                upload_file(ftp_socket, recv_socket, local_path, ftp_path)
            case "exit":
                break
            case _:
                print(dedent('''
                    Supported commands:
                    list
                    get
                    upload
                    exit
                '''))

finally:
    ftp_socket.close()
    recv_socket.close()