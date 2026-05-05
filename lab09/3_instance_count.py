import random
import socket
import threading
import time
from tkinter import *
from tkinter import ttk

timeout_mult = 3
lo_port = 11000
hi_port = 12000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
for i in range(10):
    try:
        port = random.randint(lo_port, hi_port)
        sock.bind(('', port))
        print('bound to port', port)
        break
    except OSError:
        continue
else:
    print("couldn't find free port in 10 attempts, exiting")
    exit(0)

def addrtos(addr):
    return f"{addr[0]}:{addr[1]}"

instances = {}
def _send_thread():
    global instances
    while True:
        for instance in instances:
            instances[instance] += 1
        timed_out_instances = [instance for instance in instances if instances[instance] > timeout_mult]
        for instance in timed_out_instances:
            print(instance, "hasn't responded to last", timeout_mult, "pings, removing from list")
            del instances[instance]
        clients.set(list(instances.keys()))
        header.set(f"{len(instances)} copies running")
        print("sending ping")
        for port in range(lo_port, hi_port + 1):
            sock.sendto(b'ping', ('<broadcast>', port))
        time.sleep(int(seconds.get()))

def _receive_thread():
    global instances
    while True:
        data, addr = sock.recvfrom(1024)
        addrs = addrtos(addr)
        if data == b'ping':
            print("received ping from", addrtos(addr))
            sock.sendto(b'pong', addr)
        elif data == b'pong':
            if addrs not in instances:
                instances[addrs] = 0
                clients.set(list(instances.keys()))
                header.set(f"{len(instances)} copies running")
            instances[addrs] = 0
        elif data == b'close':
            print("received close from", addrtos(addr))
            del instances[addrs]
            clients.set(list(instances.keys()))
            header.set(f"{len(instances)} copies running")
        else:
            print("received unexpected message from", addrtos(addr), ":", data.decode())

root = Tk()
root.geometry("500x500")
root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1)

header = StringVar(root, value="0 copies running")
label1 = ttk.Label(root, textvariable=header)
label1.grid(row=0, column=0, columnspan=2, padx=8, pady=8)

label2 = ttk.Label(root, text="Send messages every X seconds:")
label2.grid(row=1, column=0)

seconds = ttk.Spinbox(root, from_=1, to=60, increment=1)
seconds.set(5)
seconds.grid(row=1, column=1)

clients = Variable(value=[])
client_list = Listbox(root, listvariable=clients)
client_list.grid(row=2, column=0, columnspan=2, sticky='NSEW', padx=10, pady=(4, 4))

v_scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=client_list.yview)
client_list['yscrollcommand'] = v_scrollbar.set
v_scrollbar.grid(row=2, column=2, sticky="NS", pady=(4, 4))

threading.Thread(target=_send_thread, daemon=True).start()
threading.Thread(target=_receive_thread, daemon=True).start()
root.mainloop()

for port in range(lo_port, hi_port + 1):
    sock.sendto(b'close', ('<broadcast>', port))