import multiprocessing
import os
from socket import *
from subprocess import Popen, PIPE
from sys import argv
import pathlib

root = pathlib.Path(os.getcwd()).absolute()
format_string = "%a, %d %b %Y %H:%M:%S %z"
server_name = "hw3/1.0"

def process_request(conn):
    while True:
        cmd = conn.recv(1024).decode()
        if len(cmd) == 0:
            print("Closing connection")
            conn.close()
            break
        print("Received command: " + cmd)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        while process.poll() is None:
            conn.send(process.stdout.read())
            conn.send(process.stderr.read())
        conn.send(b"Process finished with return code " + str(process.returncode).encode())

if argv[1] == "s":
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', int(argv[2])))
    server_socket.listen(1)
    try:
        while True:
            conn, addr = server_socket.accept()
            thread = multiprocessing.Process(target=process_request, args=(conn,))
            thread.start()
    except KeyboardInterrupt:
        server_socket.close()
elif argv[1] == "c":
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(('127.0.0.1', int(argv[2])))

    while True:
        client_socket.send(input("> ").encode())
        while True:
            s = client_socket.recv(1024).decode()
            print(s)
            if s.startswith("Process finished with return code"):
                break
else:
    print('run this command with "s (port)" or "c (port)"')