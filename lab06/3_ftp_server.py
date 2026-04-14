from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
from pathlib import Path
from socket import *
import os

root = Path(os.getcwd())
debug = True

def _send(conn, c):
    if debug:
        print('>', c.decode().strip())
    conn.send(c)

def _recv(conn):
    res = conn.recv(1024).strip().decode()
    if debug:
        print('<', res)
    return res

def ftp_mainloop(conn):
    logged_in = 0
    data_host = ""
    data_port = 0
    current_dir = root
    _send(conn, b'220 Welcome to FTP!\r\n')
    while True:
        r = _recv(conn)
        for line in r.split('\r\n'):
            if ' ' not in line:
                command = line
                argument = ''
            else:
                command, argument = line.split(' ', 1)
            if command == "QUIT":
                response = b'200 Closing connection\r\n'
                _send(conn, response)
                conn.close()
                return
            elif command == "USER":
                logged_in = 1
                response = b'331 Please, specify the password.\r\n'
                _send(conn, response)
            elif command == "PASS":
                logged_in = 2
                response = b'230 Login successful.\r\n'
                _send(conn, response)
            elif command == "PWD":
                if logged_in != 2:
                    _send(conn, b'530 Not logged in\r\n')
                    continue
                pwd = current_dir.relative_to(root)
                response = f'257 "{pwd}" is current directory.\r\n'
                _send(conn, response.encode())
            elif command == "CWD":
                if logged_in != 2:
                    _send(conn, b'530 Not logged in\r\n')
                    continue
                new_dir = current_dir / argument
                new_dir = new_dir.resolve()
                if not os.path.isdir(new_dir):
                    response = b"500 Couldn't open the directory.\r\n"
                elif not new_dir.is_relative_to(root):
                    response = b"500 Couldn't open the directory.\r\n"
                else:
                    current_dir = new_dir
                    response = b'250 CWD command successful\r\n'
                _send(conn, response)
            elif command == "CDUP":
                if logged_in != 2:
                    _send(conn, b'530 Not logged in\r\n')
                    continue
                new_dir = current_dir.parent
                if not new_dir.is_relative_to(root):
                    response = b"500 Couldn't open the directory.\r\n"
                else:
                    response = b'250 CDUP command successful\r\n'
                _send(conn, response)
            elif command == "PORT":
                if logged_in != 2:
                    conn.send(b'530 Not logged in\r\n')
                    continue
                try:
                    ip0, ip1, ip2, ip3, port0, port1 = map(int, argument.split(','))
                    data_host = f"{ip0}.{ip1}.{ip2}.{ip3}"
                    data_port = port0 * 256 + port1
                    response = '200 PORT command successful\r\n'
                except ValueError:
                    response = '500 Illegal PORT command\r\n'
                _send(conn, response.encode())
            elif command == "NLST":
                if logged_in != 2:
                    _send(conn, b'530 Not logged in\r\n')
                    continue
                if data_port == 0:
                    _send(conn, b'425 Use PORT command first\r\n')
                    continue
                _send(conn, b'150 Starting data transfer.\r\n')
                data_connection = socket(AF_INET, SOCK_STREAM)
                data_connection.connect((data_host, data_port))
                for filename in current_dir.iterdir():
                    _send(data_connection, filename.name.encode() + b'\r\n')
                data_connection.close()
                _send(conn, b'250 Data transfer completed.\r\n')
                data_host = ""
                data_port = 0
            elif command == "RETR":
                if logged_in != 2:
                    _send(conn, b'530 Not logged in\r\n')
                    continue
                if data_port == 0:
                    _send(conn, b'425 Use PORT command first\r\n')
                    continue
                file = current_dir / argument
                file = file.resolve()
                if not file.is_file():
                    _send(conn, b'550 File not found.\r\n')
                    continue
                _send(conn, b'150 Starting data transfer.\r\n')
                data_connection = socket(AF_INET, SOCK_STREAM)
                data_connection.connect((data_host, data_port))
                with file.open('rb') as f:
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        _send(data_connection, data)
                data_connection.close()
                _send(conn, b'250 Data transfer completed.\r\n')
                data_host = ""
                data_port = 0
            elif command == "STOR":
                if logged_in != 2:
                    _send(conn, b'530 Not logged in\r\n')
                    continue
                if data_port == 0:
                    _send(conn, b'425 Use PORT command first\r\n')
                    continue
                file = current_dir / argument
                file = file.resolve()
                if not file.parent.is_dir():
                    _send(conn, b"553 Directory doesn't exisst\r\n")
                    continue
                _send(conn, b'150 Starting data transfer.\r\n')
                data_connection = socket(AF_INET, SOCK_STREAM)
                data_connection.connect((data_host, data_port))
                data_connection.settimeout(1)
                with file.open('wb') as f:
                    while True:
                        data = data_connection.recv(1024)
                        if not data:
                            break
                        if debug:
                            print('<', data)
                        f.write(data)
                data_connection.close()
                _send(conn, b'250 Data transfer completed.\r\n')
                data_host = ""
                data_port = 0
            else:
                _send(conn, b'500 Unknown command.\r\n')


ftp_socket = socket(AF_INET, SOCK_STREAM)
ftp_socket.bind(('127.0.0.1', 21))
ftp_socket.listen(1)
print('Listening for connections...')

with ThreadPool(8) as thread_pool:
    while True:
        conn, addr = ftp_socket.accept()
        print('Accepted connection from ', addr)
        #thread_pool.apply_async(ftp_mainloop, args=(conn,))
        ftp_mainloop(conn)