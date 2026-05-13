import socket
import struct
import threading
from tkinter import *

root = Tk()
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.geometry('600x600')
root.resizable(False, False)
root.title('Draw (server window)')

canvas = Canvas(root, width=600, height=600, bg='white')
canvas.grid(row=0, column=0)

drawing = False
previous_coords = (-1, -1)
def on_mouse_move(event):
    global drawing, previous_coords, conns
    if drawing:
        canvas.create_line(previous_coords[0], previous_coords[1], event.x, event.y, fill='black')
        previous_coords = (event.x, event.y)
        for conn in conns.values():
            conn.send(struct.pack("!IBII", 0, 1, event.x, event.y))
def on_click(event):
    global drawing, previous_coords, conns
    drawing = True
    previous_coords = (event.x, event.y)
    for conn in conns.values():
        conn.send(struct.pack("!IBII", 0, 0, event.x, event.y))
def on_release(event):
    global drawing
    drawing = False
canvas.bind('<B1-Motion>', on_mouse_move)
canvas.bind('<Button-1>', on_click)
canvas.bind('<ButtonRelease-1>', on_release)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 8080))
server.listen()
conns = {}

def conn_loop(conn_no, conn):
    prev_x, prev_y = -1, -1
    while True:
        try:
            data = conn.recv(1024)
        except IOError:
            del conns[conn_no]
            break
        is_cont, x, y = struct.unpack("!BII", data)
        if is_cont:
            canvas.create_line(prev_x, prev_y, x, y, fill='black')
        prev_x, prev_y = x, y

        for other_conn_no in conns:
            if other_conn_no != conn_no:
                conns[other_conn_no].send(struct.pack("!I", conn_no) + data)

def server_loop():
    global conns
    print("Started server loop")
    next_conn_no = 1
    while True:
        conn, addr = server.accept()
        print("Accepted connection from", addr)
        conns[next_conn_no] = conn
        threading.Thread(target=conn_loop, args=(next_conn_no, conn)).start()
        next_conn_no += 1
threading.Thread(target=server_loop, daemon=True).start()

root.mainloop()