import socket
from sys import argv

socket.setdefaulttimeout(1)

if len(argv) == 1:
    print('Provide an IP address')
    exit(0)
ip_address = argv[1]
if len(argv) > 2:
    lo_port = max(0, int(argv[2]))
    hi_port = min(65535, int(argv[3]))
else:
    lo_port = 0
    hi_port = 65535

for port in range(lo_port, hi_port+1):
    print("Testing port", port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip_address, port))
        print("Connected to port", port)
        s.close()
    except:
        pass