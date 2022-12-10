import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk

HOST = socket.gethostname()
PORT = 1234

DARK_GREY = '#121212'
MEDIUM_GREY = '#1F1B24'
OCEAN_BLUE = '#464EB8'
WHITE = "white"
FONT = ("Helvetica", 17)
BUTTON_FONT = ("Helvetica", 15)
SMALL_FONT = ("Helvetica", 13)

# Creating a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
active_user = ['GROUP']
is_connect = False

def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)

def connect():
    # try except block
    global is_connect
    if not is_connect:
        try:
            # Connect to the server
            client.connect((HOST, PORT))
            print("Successfully connected to server")
            add_message("[SERVER] Successfully connected to the server")
            is_connect = not is_connect
        except:
            messagebox.showerror("Unable to connect to server", f"Unable to connect to server {HOST} {PORT}")

    username = username_textbox.get()
    if username == '':
        messagebox.showerror("Invalid username", "Username cannot be empty")
        return
    else:
        client.sendall(username.encode())
        response = client.recv(2048).decode()
        if response == '/duplicate':
            messagebox.showerror("Invalid username", "Username already chose")
            return
    global active_user
    list_user = client.recv(2048).decode('utf-8')
    active_user = list_user.split('/')
    active_user.append('GROUP')
    active_header['value'] = active_user
    threading.Thread(target=listen_for_messages_from_server, args=(client, )).start()
    username_textbox.config(state=tk.DISABLED)
    username_button.config(state=tk.DISABLED)

def send_message():
    message = message_textbox.get()
    if message != '':
        message = active_header.get() + '/' + message
        client.sendall(message.encode())
        message_textbox.delete(0, len(message))
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")

root = tk.Tk()
root.geometry("600x600")
root.title("Messenger Client")
root.resizable(False, False)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

top_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
top_frame.grid(row=0, column=0, sticky=tk.NSEW)

middle_frame = tk.Frame(root, width=600, height=400, bg=MEDIUM_GREY)
middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

bottom_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)

username_label = tk.Label(top_frame, text="Enter username:", font=FONT, bg=DARK_GREY, fg=WHITE)
username_label.pack(side=tk.LEFT, padx=10)

username_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=23)
username_textbox.pack(side=tk.LEFT)

username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=connect)
username_button.pack(side=tk.LEFT, padx=15)

active_header = ttk.Combobox(bottom_frame, values = active_user, width = 10, height= 26.5)
active_header.pack(side=tk.LEFT, padx= 10)
active_header.set('GROUP')

message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=28)
message_textbox.pack(side=tk.LEFT, padx=10)

message_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=send_message)
message_button.pack(side=tk.LEFT, padx=10)

message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=WHITE, width=67, height=26.5)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP)

def listen_for_messages_from_server(client):
    while 1:
        message = client.recv(2048).decode('utf-8')
        if 'SERVER~' in message and 'added to the chat' in message:
            new_username = message[7:-18]
            if new_username not in active_user:
                active_user.append(new_username)
                active_header['value'] = active_user
        if message != '':
            username = message.split("~")[0]
            content = message.split('~')[1]
            add_message(f"[{username}] {content}")
        else:
            messagebox.showerror("Error", "Message recevied from client is empty")

# main function
def main():
    root.mainloop()
    
if __name__ == '__main__':
    main()