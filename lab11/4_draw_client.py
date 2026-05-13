import socket
import struct
import threading
from tkinter import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('', 8080))

root = Tk()
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
root.geometry('600x600')
root.resizable(False, False)
root.title('Draw (client window)')

canvas = Canvas(root, width=600, height=600, bg='white')
canvas.grid(row=0, column=0)

drawing = False
previous_coords = (-1, -1)
def on_mouse_move(event):
    global drawing, previous_coords
    if drawing:
        canvas.create_line(previous_coords[0], previous_coords[1], event.x, event.y, fill='black')
        previous_coords = (event.x, event.y)
        sock.send(struct.pack("!BHH", 1, event.x, event.y))
def on_click(event):
    global drawing, previous_coords
    drawing = True
    previous_coords = (event.x, event.y)
    sock.send(struct.pack("!BHH", 0, event.x, event.y))
def on_release(event):
    global drawing
    drawing = False
canvas.bind('<B1-Motion>', on_mouse_move)
canvas.bind('<Button-1>', on_click)
canvas.bind('<ButtonRelease-1>', on_release)

def recv_loop():
    previous_coords = {}
    while True:
        data = sock.recv(1024)
        if data == b'':
            continue
        source, is_cont, x, y = struct.unpack("!IBHH", data)
        if is_cont and source in previous_coords:
            prev_x, prev_y = previous_coords[source]
            canvas.create_line(prev_x, prev_y, x, y, fill='black')
        previous_coords[source] = (x, y)
threading.Thread(target=recv_loop, daemon=True).start()

root.mainloop()