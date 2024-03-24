import json
import socket
import sys
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 4096

class ChatClient:
    def __init__(self):
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = ""
        try:
            self.tcp_client_socket.connect((SERVER_HOST, SERVER_PORT))
            print("connected to the server\n")
        except socket.error as err:
            print(err)
            sys.exit(1)

    def init_chat(self):
        input_operation = input("do you want to create chat room or join chat room? input 'create' or 'join' > ")
        input_room_name = input("input room name you want to create or join > ")
        input_password = input("input password of room > ")
        input_participants_max_num = "0"
        if (input_operation == "create"):
            input_participants_max_num = input("input maximum number of participants > ")

        request_data = self.create_request_data(
            input_operation,
            input_room_name,
            input_password,
            input_participants_max_num
        )

        try:
            self.tcp_client_socket.sendall(request_data)
            self.tcp_client_socket.settimeout(2)

            try:
                self.username = self.tcp_client_socket.recv(BUFFER_SIZE).decode("utf-8")
                print(self.username)
            except socket.timeout:
                print('socket timeout, ending listening for server messages')

        finally:
            self.tcp_client_socket.close()

    def create_request_data(self, operation, room_name, password, participants_max_num):
        _operation = 1 if operation == "create" else 2
        room_name_len = len(room_name)
        payload = json.dumps({
            'password': password,
            'participants_max_num': int(participants_max_num),
        })
        payload_len = len(payload)

        return room_name_len.to_bytes(1, "big") + \
            _operation.to_bytes(1, "big") + \
            payload_len.to_bytes(30, "big") + \
            room_name.encode("utf-8") + \
            payload.encode("utf-8")

    def run(self):
        self.init_chat()

if __name__ == "__main__":
    chat_client = ChatClient()
    chat_client.run()
