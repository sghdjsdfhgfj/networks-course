import os
from socket import *
from tkinter import *
from tkinter import ttk

debug = True

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


root = Tk()

recv_socket = socket(AF_INET, SOCK_STREAM)
recv_socket.bind(('127.0.0.1', 8080))
recv_socket.listen(1)
ftp_socket: socket | None = None

client_host = StringVar(value="127.0.0.1")
username = StringVar(value="TestUser")
password = StringVar()
files = Variable(value=[])
current_dir = StringVar()
selected_file = StringVar()

def connect():
    global ftp_socket
    if ftp_socket is not None:
        ftp_socket.close()
    host = client_host.get()
    ftp_socket = socket(AF_INET, SOCK_STREAM)
    ftp_socket.connect((host, 21))
    _recv(ftp_socket)
    _send(ftp_socket, b'USER ' + username.get().encode() + b'\r\n')
    _recv(ftp_socket)
    _send(ftp_socket, b'PASS ' + password.get().encode() + b'\r\n')
    if _success(ftp_socket):
        list_files()
    else:
        ftp_socket = None

def get_data_connection(ftp_socket, cmd):
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

def list_files():
    if ftp_socket is None:
        return
    conn = get_data_connection(ftp_socket, b'NLST\r\n')
    if not conn:
        return
    c_files = []
    if current_dir.get():
        c_files.append("..")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        if debug:
            print('<', data.decode().strip())
        c_files.extend(data.decode().strip().split("\n"))
    conn.close()
    _recv(ftp_socket)
    files.set(c_files)

def select_file(event):
    listbox = event.widget
    selected_i = listbox.curselection()[0]
    selected = listbox.get(selected_i)
    selected_file.set(selected)

def cd_or_edit(event):
    if ftp_socket is None:
        return
    if selected_file.get() == "":
        return
    selected = selected_file.get()
    if selected == "..":
        _send(ftp_socket, b'CDUP\r\n')
        if _success(ftp_socket):
            current_dir.set("/".join(current_dir.get().split("/")[:-1]))
            selected_file.set("")
            list_files()
        return

    _send(ftp_socket, b'CWD ' + selected.encode() + b'\r\n')
    if _success(ftp_socket):
        current_dir.set(current_dir.get() + "/" + selected)
        selected_file.set("")
        list_files()
    else:
        open_edit_window()

def create_file():
    if ftp_socket is None:
        return
    if selected_file.get() == "":
        return
    ftp_path = selected_file.get()
    conn = get_data_connection(ftp_socket, b'STOR ' + ftp_path.encode() + b'\r\n')
    if not conn:
        return
    conn.close()
    _recv(ftp_socket)
    list_files()

def delete_file():
    if ftp_socket is None:
        return
    if selected_file.get() == "":
        return
    ftp_path = selected_file.get()
    _send(ftp_socket, b'DELE ' + ftp_path.encode() + b'\r\n')
    if not _success(ftp_socket):
        return
    list_files()

def get_file(ftp_path):
    _send(ftp_socket, b'TYPE I\r\n')
    _recv(ftp_socket)
    conn = get_data_connection(ftp_socket, b'RETR ' + ftp_path.encode() + b'\r\n')
    if not conn:
        return
    contents = b''
    while True:
        data = conn.recv(1024)
        if not data:
            break
        if debug:
            print('<', data)
        contents += data
    conn.close()
    _recv(ftp_socket)
    return contents.decode()

def upload_file(ftp_path, contents):
    conn = get_data_connection(ftp_socket, b'STOR ' + ftp_path.encode() + b'\r\n')
    if not conn:
        return
    for i in range(0, len(contents), 1024):
        data = contents[i:i+1024]
        conn.send(data)
        if debug:
            print('>', data)
    conn.close()
    _recv(ftp_socket)

def open_edit_window():
    if ftp_socket is None:
        return
    if selected_file.get() == "":
        return

    contents = get_file(selected_file.get())
    if contents is None:
        return

    window = Toplevel()
    window.title((current_dir.get() + "/" + selected_file.get())[1:])
    window.geometry('800x600')
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=1)
    window.rowconfigure(0, weight=1)

    contents_editor = Text(window)
    contents_editor.insert(END, contents)
    scroll = Scrollbar(window)
    contents_editor.configure(yscrollcommand=scroll.set)
    contents_editor.grid(row=0, column=0, columnspan=2, sticky='NSEW', padx=10, pady=10)
    scroll.config(command=contents_editor.yview)
    scroll.grid(row=0, column=2, sticky='NS')

    def _save():
        upload_file(selected_file.get(), contents_editor.get("1.0", "end").encode())
    def _exit():
        window.destroy()

    save_button = ttk.Button(window, text="Save", command=_save)
    save_button.grid(row=1, column=0, sticky='EW', pady=5, padx=10)
    close_button = ttk.Button(window, text="Exit", command=_exit)
    close_button.grid(row=1, column=1, sticky='EW', pady=5, padx=10)


root.title('FTP client')
root.geometry('800x600')
root.columnconfigure(1, weight=1)
root.rowconfigure(4, weight=1)

ttk.Label(root, text='Client host:').grid(row=0, column=0, pady=4)
host_entry = ttk.Entry(root, textvariable=client_host)
host_entry.grid(row=0, column=1, sticky='EW')

ttk.Label(root, text='Username:').grid(row=1, column=0, pady=4)
username_entry = ttk.Entry(root, textvariable=username)
username_entry.grid(row=1, column=1, sticky='EW')

ttk.Label(root, text='Password:').grid(row=2, column=0, pady=4)
password_entry = ttk.Entry(root, textvariable=password)
password_entry.grid(row=2, column=1, sticky='EW')

connect_button = ttk.Button(root, text='Connect', command=connect)
connect_button.grid(row=1, column=2)

ttk.Label(root, text='Directory:').grid(row=3, column=0, pady=(30, 4))
file_entry = ttk.Entry(root, textvariable=current_dir)
file_entry.grid(row=3, column=1, columnspan=3, sticky='EW', pady=(30, 4))

files_list = Listbox(root, listvariable=files)
files_list.grid(row=4, column=0, columnspan=3, sticky='NSEW', padx=10, pady=(4, 4))
files_list.bind('<<ListboxSelect>>', select_file)
files_list.bind('<Double-Button>', cd_or_edit)

v_scrollbar = ttk.Scrollbar(root, orient=VERTICAL, command=files_list.yview)
files_list['yscrollcommand'] = v_scrollbar.set
v_scrollbar.grid(row=4, column=4, sticky="NS", pady=(4, 4))

ttk.Label(root, text='File:').grid(row=5, column=0, rowspan=4)
file_entry = ttk.Entry(root, textvariable=selected_file)
file_entry.grid(row=5, column=1, rowspan=4, padx=4, sticky='EW')

create_button = ttk.Button(root, text='Create', command=create_file)
create_button.grid(row=5, column=2)

retrieve_button = ttk.Button(root, text='Edit', command=open_edit_window)
retrieve_button.grid(row=6, column=2)

delete_button = ttk.Button(root, text='Delete', command=delete_file)
delete_button.grid(row=8, column=2)

root.mainloop()

if ftp_socket is not None:
    ftp_socket.close()
recv_socket.close()