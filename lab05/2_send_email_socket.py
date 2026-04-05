import base64
import ssl
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv

host_name = "smtp.gmail.com"
sender = "reas.qf0@gmail.com"
with open("password.txt") as f:
    password = f.read().strip()

recipient = argv[1]
contents_file = argv[2]
if not contents_file.endswith(".txt") and not contents_file.endswith(".html"):
    print('contents file should be a txt or html file')
    exit(1)

context = ssl.create_default_context()
smtp_socket = socket(AF_INET, SOCK_STREAM)
smtp_socket.connect((host_name, 465))
ssock = context.wrap_socket(smtp_socket, server_hostname=host_name)

print(ssock.recv(1024).decode().strip())
ssock.send(b"HELO hw5\r\n")
print(ssock.recv(1024).decode().strip())
ssock.send(b"AUTH PLAIN " + base64.b64encode(b"\0" + sender.encode() + b"\0" + password.encode()) + b"\r\n")
print(ssock.recv(1024).decode().strip())
ssock.send(b"MAIL FROM: <" + sender.encode() + b">\r\n")
print(ssock.recv(1024).decode().strip())
ssock.send(b"RCPT TO: <" + recipient.encode() + b">\r\n")
print(ssock.recv(1024).decode().strip())
ssock.send(b"DATA\r\n")
print(ssock.recv(1024).decode().strip())

ssock.send(b"MIME-Version: 1.0\r\n")
if contents_file.endswith(".txt"):
    ssock.send(b"Content-Type: text/plain\r\n")
elif contents_file.endswith(".html"):
    ssock.send(b"Content-Type: text/html\r\n")
ssock.send(b"Content-Transfer-Encoding: 8bit\r\n\r\n")
with open(contents_file, "rb") as f:
    ssock.send(f.read())
ssock.send(b"\r\n.\r\n")
print(ssock.recv(1024).decode().strip())

ssock.close()
smtp_socket.close()