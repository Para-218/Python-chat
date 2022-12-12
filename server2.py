import socket
import threading
import time

HOST = socket.gethostname()
PORT = 1234 # You can use any port between 0 to 65535
LISTENER_LIMIT = 5

active_clients = [] # List of all currently connected users
dictionary_active_clients = {} # Dict to find client_socket
fileTransferCondition = threading.Condition()

# Function for file transfer
def fileTransfer(client, username):
    #client.send('send_filename'.encode())
    fileName = client.recv(2048).decode()
    #client.send('send_dest_user'.encode())
    dest_user = client.recv(2048).decode()
    #client.send('send_data'.encode())
    remaining = int.from_bytes(client.recv(4),'big')
    f = open(fileName,"wb")
    while remaining:
        data = client.recv(min(remaining,4096))
        remaining -= len(data)
        f.write(data)
    f.close()
    print('Receive file success')
    if dest_user == 'GROUP': #send file to all active user
        for user in active_clients:
            if user != username:
                memberClient = dictionary_active_clients[user]
                #send notify message
                memberClient.send("/receiveFile".encode())
                time.sleep(0.2)
                #send file name
                memberClient.send(bytes(fileName,"utf-8"))
                time.sleep(0.2)
                #send source user
                memberClient.send(bytes(username,"utf-8"))
                time.sleep(0.2)
                with open(fileName,'rb') as f:
                    data = f.read()
                    dataLen = len(data)
                    memberClient.send(dataLen.to_bytes(4,'big'))
                    memberClient.send(data)

# Function to listen for upcoming messages from a client
def listen_for_messages(client, username):
    while 1:
        message = client.recv(2048).decode('utf-8')
        if message == '/fileTransfer':
            fileTransfer(client, username)
            continue
        elif 'GROUP/' in message:
            final_msg = username + '~' + message.split('/')[1]
            send_messages_to_all(final_msg)
        else:
            dest_user = message.split('/')[0]
            final_msg = username + ' whisper to ' + dest_user + '~' + message.split('/')[1]
            send_message_to_client(dictionary_active_clients[dest_user], final_msg)
            send_message_to_client(dictionary_active_clients[username], final_msg)

# Function to send message to a single client
def send_message_to_client(client, message):
    client.sendall(message.encode())

# Function to send any new message to all the active clients
def send_messages_to_all(message):
    for user in active_clients:
        send_message_to_client(dictionary_active_clients[user], message)

# Function to handle client
def client_handler(client):
    # Server will listen for client message that will contain the username
    while 1:
        username = client.recv(2048).decode('utf-8')
        if username not in active_clients:
            client.send('/accept'.encode())
            active_clients.append(username)
            dictionary_active_clients[username] = client
            #send list active user
            client.send(('/'.join(active_clients)).encode())
            time.sleep(0.5)
            prompt_message = "SERVER~" + f"{username} added to the chat"
            send_messages_to_all(prompt_message)
            break
        else:
            client.send('/duplicate'.encode())
    threading.Thread(target=listen_for_messages, args=(client, username, )).start()

# Main function
def main():
    # Creating the socket class object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Creating a try catch block
    try:
        server.bind((HOST, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")
    # Set server limit
    server.listen(LISTENER_LIMIT)

    # This while loop will keep listening to client connections
    while 1:
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")
        threading.Thread(target=client_handler, args=(client, )).start()

if __name__ == '__main__':
    main()