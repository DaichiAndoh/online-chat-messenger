import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 4096

class ChatServer:
    def __init__(self):
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((SERVER_HOST, SERVER_PORT))
        print("[SERVER] Server is listening...\n")

    def handle_client(self, data, client_address):
        username_len = data[0]
        username = data[1:1 + username_len].decode("utf-8")
        message = data[1 + username_len:].decode("utf-8")
        print(f"[{username}] {message}")
        self.relay_message(data, client_address)

    def relay_message(self, data, sender_address):
        for address in self.clients:
            if address != sender_address:
                self.server_socket.sendto(data, address)

    def run(self):
        while True:
            data, client_address = self.server_socket.recvfrom(BUFFER_SIZE)
            if client_address not in self.clients:
                print(f"[SERVER] New client connected: {client_address}\n")
                self.clients[client_address] = threading.Thread(
                    target=self.handle_client, args=(data, client_address)
                )
                self.clients[client_address].start()
            else:
                self.handle_client(data, client_address)

if __name__ == "__main__":
    chat_server = ChatServer()
    chat_server.run()
