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
        self.participants = [owner]

class Client:
    def __init__(self, connection, tcp_client_address):
        ip, port = tcp_client_address
        self.connection = connection
        self.username = ip + ":" + str(port)
        self.ip = None
        self.port = None
        self.lastSentDate = None

class ChatServer:
    def __init__(self):
        self.clients = {}
        self.rooms = {}

        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.tcp_server_socket.listen(1)

        self.udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server_socket.bind((SERVER_HOST, SERVER_PORT))
        print("server is listening...\n")

    def init_chat(self, client):
        request_header = client.connection.recv(BUFFER_SIZE)

        room_name_len = request_header[0]
        operation = request_header[1]
        operation_payload_len = request_header[2:31]

        room_name = request_header[32:32 + room_name_len].decode("utf-8")
        operation_payload = json.loads(request_header[32 + room_name_len:].decode("utf-8"))

        result = ""
        if operation == 1:
            result = self.create_room(client, room_name, operation_payload)
        elif operation == 2:
            result = self.join_room(client, room_name, operation_payload)

        response_data = {
            "status": 1 if result == "" else 0,
            "payload": client.username if result == "" else result,
        }
        client.connection.sendall(json.dumps(response_data).encode())

    def create_room(self, client, room_name, operation_payload):
        room = ChatRoom(
            room_name,
            client.username,
            operation_payload["password"],
            operation_payload["participants_max_num"]
        )
        self.rooms[room_name] = room
        return ""

    def join_room(self, client, room_name, operation_payload):
        try:
            room = self.rooms[room_name]
            if room.password == operation_payload["password"] and len(room.participants) < room.participants_max_num:
                self.rooms[room_name].participants.append(client.username)
                return ""
            else:
                return "password is not correct or room participants limit has been reached"
        except KeyError:
            return "room is not found"

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

        client = self.clients[username]
        room = self.rooms[room_name]

        client.ip = client_address[0]
        client.port = client_address[1]
        client.lastSentDate = datetime.now()
        print(f"[{username}] {message}")
        self.relay_message(message, client, room)

    def relay_message(self, message, client, room):
        standard_date = datetime.now() - timedelta(seconds=30)
        room_owner = self.clients[room.owner]

        if room_owner.lastSentDate < standard_date:
            for username in room.participants:
                participant = self.clients[username]
                self.udp_server_socket.sendto(
                    self.create_response_data(0, "Server Alert", room.room_name, "room is closed"),
                    (participant.ip, participant.port)
                )
                self.clients.pop(participant.username)
            self.rooms.pop(room.room_name)
        else:
            for username in room.participants:
                participant = self.clients[username]
                if participant.username != client.username and participant.lastSentDate > standard_date:
                    self.udp_server_socket.sendto(
                        self.create_response_data(1, username, room.room_name, message),
                        (participant.ip, participant.port)
                    )
                elif participant.username != client.username and participant.lastSentDate < standard_date:
                    self.udp_server_socket.sendto(
                        self.create_response_data(0, "Server Alert", room.room_name, "time out error"),
                        (participant.ip, participant.port)
                    )
                    room.participants.pop(room.participants.index(participant.username))
                    self.clients.pop(participant.username)

    def create_response_data(self, status, username, room_name, message):
        return json.dumps({
            "status": status,
            "username": username,
            "room_name": room_name,
            "message":  message,
        }).encode()

    def run_udp_socket(self):
        while True:
            data, client_address = self.udp_server_socket.recvfrom(BUFFER_SIZE)
            threading.Thread(target=self.handle_client, args=(data, client_address)).start()

if __name__ == "__main__":
    chat_server = ChatServer()
    threading.Thread(target=chat_server.run_tcp_socket).start()
    threading.Thread(target=chat_server.run_udp_socket).start()
