import socket
import threading
import time

HOST = socket.gethostname()
PORT = 10000
USER_LIMIT = 5
active_clients = []
dictionary_active_clients = {}

def delete_user(client_socket, username):
    send_message_to_client(client_socket, "exit_accept")
    client_socket.close()
    active_clients.remove((username, client_socket))
    message = 'SERVER: ' + username + ' EXIT CHANNEL'
    send_message_to_all(message)

def listen_for_message(client_socket, username):
    while True:
        response = client_socket.recv(2048).decode()
        if response != '':
            if response == "exit":
                delete_user(client_socket, username)
                break
            message = username + ':' + response
            send_message_to_all(message)
        else:
            print(f"The message send from client {username} is empty")

def send_message_to_client(client_socket, message):
    client_socket.sendall(message.encode())

def send_message_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)

def client_handler(client_socket):
    while True:
        username = client_socket.recv(2048).decode()
        if username != '':
            message = '/deny'
            if username not in active_clients:
                active_clients.append(username)
                dictionary_active_clients[username] = client_socket
                client_socket.sendall(('/accept').encode())
                break
            client_socket.sendall(message.encode())
        else:
            print('Client username is empty')
    message = "SERVER: " + f"{username}" + " added to the chat"
    send_message_to_all('new_user')
    send_message_to_all(username)
    send_message_to_all(message)
    threading.Thread(target= listen_for_message, args=(client_socket, username)).start()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(('',PORT))
    except:
        print("Fail to bind ")
        return
    server_socket.listen(USER_LIMIT)
    
    while True:
        client_socket, address = server_socket.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")
        threading.Thread(target = client_handler, args=(client_socket, )).start()

if __name__ == '__main__':
    main()