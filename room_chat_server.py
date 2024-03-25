import json
import socket
import threading
from datetime import datetime, timedelta

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 4096

class ChatRoom:
    def __init__(self, room_name, owner, password, participants_max_num):
        self.room_name = room_name
        self.owner = owner
        self.participants_max_num = participants_max_num
        self.password = password
        self.participants = []

class Client:
    def __init__(self, connection, tcp_client_address):
        ip, port = tcp_client_address
        self.connection = connection
        self.username = ip + ':' + str(port)
        self.ip = None
        self.port = None
        self.lastSentDate = None

class ChatServer:
    def __init__(self):
        self.clients = {}
        self.rooms = {}

        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.udp_server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.tcp_server_socket.listen(1)
        print("server is listening...\n")

    def init_chat(self, client):
        request_header = client.connection.recv(BUFFER_SIZE)

        room_name_len = request_header[0]
        operation = request_header[1]
        operation_payload_len = request_header[2:31]

        room_name = request_header[32:32 + room_name_len].decode("utf-8")
        operation_payload = json.loads(request_header[32 + room_name_len:].decode("utf-8"))

        if operation == 1:
            self.create_room(client, room_name, operation_payload)
        elif operation == 2:
            self.join_room(client, room_name, operation_payload)

        client.connection.sendall(client.username.encode())

    def create_room(self, client, room_name, operation_payload):
        room = ChatRoom(
            room_name,
            client.username,
            operation_payload["password"],
            operation_payload["participants_max_num"]
        )
        room.participants = [client.username]
        self.rooms[room_name] = room

    def join_room(self, client, room_name, operation_payload):
        try:
            room = self.rooms[room_name]
            if room.password == operation_payload["password"] and len(room.participants) < room.participants_max_num:
                self.rooms[room_name].participants.append(client.username)
            else:
                print("error")
        except KeyError:
            print("error")

    def run_tcp_socket(self):
        while True:
            connection, tcp_client_address = self.tcp_server_socket.accept()
            client = Client(connection, tcp_client_address)
            self.clients[client.username] = client
            threading.Thread(target=self.init_chat, args=(client,)).start()

    def handle_client(self, data, client_address):
        username_len = data[0]
        room_name_len = data[1]
        username = data[2:2 + username_len].decode("utf-8")
        room_name = data[2 + username_len:2 + username_len + room_name_len].decode("utf-8")
        message = data[2 + username_len + room_name_len:].decode("utf-8")

        if username in self.clients:
            ip, port = client_address
            self.clients[username].ip = ip
            self.clients[username].port = port
            self.clients[username].lastSentDate = datetime.now()

            print(f"[{username}] {message}")
            self.relay_message(data, username, room_name)

    def relay_message(self, data, username, room_name):
        standard_date = datetime.now() - timedelta(seconds=30)
        room = self.rooms[room_name]

        for _username in room.participants:
            client = self.clients[_username]
            if _username != username:
                self.udp_server_socket.sendto(data, (client.ip, client.port))

    def run_udp_socket(self):
        while True:
            data, client_address = self.udp_server_socket.recvfrom(BUFFER_SIZE)
            threading.Thread(target=self.handle_client, args=(data, client_address)).start()

if __name__ == "__main__":
    chat_server = ChatServer()
    threading.Thread(target=chat_server.run_tcp_socket).start()
    threading.Thread(target=chat_server.run_udp_socket).start()
