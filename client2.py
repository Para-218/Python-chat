import socket
import threading
import tkinter
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk

DARK_GREY = "#121212"
MEDIUM_GREY = "#1F1B24"
OCEAN_BLUE = "#464EB8"
WHITE = "white"
LIST = "#523b4a"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
header = "GROUP"
active_user = ['GROUP', 'Feb']

def add_message(message):
    message_box.config(state=tkinter.NORMAL)
    message_box.insert(tkinter.END, message + "\n")
    message_box.config(state=tkinter.DISABLED)

def connect():
    try:
        client_socket.connect((HOST, PORT))
        print("Success connect to server")
        add_message("[SERVER] Successfully connect to the server")
    except:
        messagebox.showerror("Fail to connect ",f"Unable to connect to server {HOST} {PORT}")
        exit(0)
    while True:
        username = username_textbox.get()
        if username != '':
            client_socket.sendall(username.encode())
            #response accept or deny
            response = client_socket.recv(2048).decode()
            if response == '/accept':
                break
            messagebox.showerror("Invalid username", "Username cannot be used")
        else:
            messagebox.showerror("Invalid username", "Username cannot be empty")
    username_textbox.config(state=tkinter.DISABLED)
    username_button.config(state=tkinter.DISABLED)

    threading.Thread(target=listen_from_server, args=(client_socket, )).start()

'''
def file_transfer(filename):
    try:
        f = open(filename,'rb')
        f.close()
    except FileNotFoundError:
        print("The requested file does not exist.")
        client_socket.send(bytes("~error~","utf-8"))
'''       
    
def send_message():
    message = message_textbox.get()
    if message != '':
        global header
        if message[0] == '[' and message[-1] == ']':
            header = message
        else:
            message = header + message
            client_socket.sendall(message.encode())
            message_textbox.delete(0, len(message))
    else:
        messagebox.showerror("Empty message","Message cannot be empty")

'''
def contact_friend():
    username = list_friend.textbox.get()
    if username != '':
        username = '/name/' + username
        client_socket.sendall(username.encode())
        list_friend.delete(0, len(username))
    else:
        messagebox.showerror("Empty username","Username cannot be empty")
'''

root = tkinter.Tk()
root.geometry("600x600")
root.title("Messenger Client")
root.resizable(False, False)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=3)
root.grid_columnconfigure(1, weight=1)

#exit_button = tkinter.Button(root, text="Exit", command=root.destroy)
#exit_button.pack(pady=20)

top_frame = tkinter.Frame(root, width=400, height=100, background=DARK_GREY)
top_frame.grid(row=0, column=0, sticky=tkinter.NSEW)

#top_frame1 = tkinter.Frame(root, width=200, height=100, background=DARK_GREY)
#top_frame1.grid(row=0, column=1, sticky=tkinter.NSEW)

middle_frame = tkinter.Frame(root, width=400, height=400, background=MEDIUM_GREY)
middle_frame.grid(row=1, column=0, sticky=tkinter.NSEW)

bottom_frame = tkinter.Frame(root, width=400, height=100, background=DARK_GREY)
bottom_frame.grid(row=2, column=0, sticky=tkinter.NSEW)

#bottom_frame1 = tkinter.Frame(root, width=200, height=100, background=DARK_GREY)
#bottom_frame1.grid(row=2, column=1, sticky=tkinter.NSEW)

#right_frame = tkinter.Frame(root, width=200, height=400, background=LIST)
#right_frame.grid(row=1, column=1, sticky=tkinter.NSEW)

#list_friend = scrolledtext.ScrolledText(right_frame, bg=LIST, fg=WHITE, width=20, height=34)
#list_friend.config(state=tkinter.DISABLED)
#list_friend.pack(side=tkinter.TOP)

username_label = tkinter.Label(top_frame, text="Enter username:", background=DARK_GREY, foreground=WHITE)
username_label.pack(side=tkinter.LEFT, padx=10)

username_textbox = tkinter.Entry(top_frame, background=MEDIUM_GREY, foreground=WHITE, width=23)
username_textbox.pack(side=tkinter.LEFT)

username_button = tkinter.Button(top_frame, text="JOIN", background=OCEAN_BLUE, foreground=WHITE, command=connect)
username_button.pack(side=tkinter.LEFT, padx=15)

active_header = ttk.Combobox(bottom_frame, values = active_user, width = 10)
active_header.pack(side=tkinter.LEFT, padx= 10)
active_header.set('GROUP')

message_textbox = tkinter.Entry(bottom_frame, background=MEDIUM_GREY, foreground=WHITE, width=38)
message_textbox.pack(side=tkinter.LEFT, padx=10)

message_button = tkinter.Button(bottom_frame, text="SEND", background=OCEAN_BLUE, foreground=WHITE, command=send_message)
message_button.pack(side=tkinter.LEFT, padx=15)

message_box = scrolledtext.ScrolledText(middle_frame, bg=MEDIUM_GREY, fg=WHITE, width=90, height=34)
message_box.config(state=tkinter.DISABLED)
message_box.pack(side=tkinter.TOP)

HOST = socket.gethostname()
PORT = 10000

def listen_from_server(client_socket):
    while True:
        message = client_socket.recv(2048).decode()
        if message != '':
            if message == 'exit_accept':
                break
            if message == 'new_user':
                new_username = client_socket.recv(2048).decode()
                active_user.append(new_username)
                active_header['value'] = active_user
            else:
                username = message.split(":")[0]
                content = message.split(":")[1]
                print(f"[{username}]:{content}")
                add_message(f"[{username}]:{content}")
        else:
            messagebox.showerror("Invalid message","Message received from server is empty")
    add_message('Exit succesfully')
    client_socket.close()
    message_textbox.config(state=tkinter.DISABLED)

def main():
    root.mainloop()

if __name__ == '__main__':
    main()