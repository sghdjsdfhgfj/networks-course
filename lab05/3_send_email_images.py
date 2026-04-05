import base64
import ssl
from socket import socket, AF_INET, SOCK_STREAM
from sys import argv

host_name = "smtp.gmail.com"
sender = b"reas.qf0@gmail.com"
with open("password.txt") as f:
    password = f.read().strip().encode()
boundary = b"gc0p4Jq0M2Yt08j34c0p"

content_types = {
    "txt": b"text/plain",
    "html": b"text/html",
    "jpg": b"image/jpeg",
    "jpeg": b"image/jpeg",
    "png": b"image/png",
}

recipient = argv[1].encode()
contents_files = argv[2:]

contents_files_supported = []
for file in contents_files:
    for ext in content_types:
        if file.endswith("." + ext):
            contents_files_supported.append(file)
            break
    else:
        print(f"{file} is not one of the supported extensions and will be ignored")
        print(f"supported extensions: {" ".join(content_types.keys())}")
contents_files = contents_files_supported
is_multipart = len(contents_files) > 1

context = ssl.create_default_context()
smtp_socket = socket(AF_INET, SOCK_STREAM)
smtp_socket.connect((host_name, 465))
ssock = context.wrap_socket(smtp_socket, server_hostname=host_name)

print(ssock.recv(1024).decode().strip())
ssock.send(b"HELO hw5\r\n")
print(ssock.recv(1024).decode().strip())
ssock.send(b"AUTH PLAIN " + base64.b64encode(b"\0" + sender + b"\0" + password) + b"\r\n")
print(ssock.recv(1024).decode().strip())
ssock.send(b"MAIL FROM: <" + sender + b">\r\n")
print(ssock.recv(1024).decode().strip())
ssock.send(b"RCPT TO: <" + recipient + b">\r\n")
print(ssock.recv(1024).decode().strip())
ssock.send(b"DATA\r\n")
print(ssock.recv(1024).decode().strip())

ssock.send(b"MIME-Version: 1.0\r\n")
if is_multipart:
    ssock.send(b"Content-Type: multipart/mixed; boundary=" + boundary + b"\r\n")
for file in contents_files:
    if is_multipart:
        ssock.send(b"\r\n--" + boundary + b"\r\n")
    ext = file.split(".")[-1]
    content_type = content_types[ext]
    ssock.send(b"Content-Type: " + content_type + b"\r\n")
    ssock.send(b"Content-Transfer-Encoding: base64\r\n\r\n")
    with open(file, "rb") as f:
        contents = base64.b64encode(f.read())
    line_length = 76
    for i in range(0, len(contents), line_length):
        ssock.send(contents[i:i+line_length] + b"\r\n")
if is_multipart:
    ssock.send(b"\r\n--" + boundary + b"--")
ssock.send(b"\r\n.\r\n")
print(ssock.recv(1024).decode().strip())

ssock.close()
smtp_socket.close()