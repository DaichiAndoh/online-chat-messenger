import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999
BUFFER_SIZE = 4096

class ChatClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = input("Enter your username: ")
        print("[CLIENT] Connected to the server.")

    def send_message(self):
        while True:
            message = input("> ")
            username_len = len(self.username)
            message_data = username_len.to_bytes(1, "big") + self.username.encode("utf-8") + message.encode("utf-8")
            self.client_socket.sendto(message_data, (SERVER_HOST, SERVER_PORT))

    def receive_messages(self):
        while True:
            data, _ = self.client_socket.recvfrom(BUFFER_SIZE)
            username_len = data[0]
            username = data[1:1 + username_len].decode("utf-8")
            message = data[1 + username_len:].decode("utf-8")
            print(f"[{username}] {message}")

    def run(self):
        send_thread = threading.Thread(target=self.send_message)
        receive_thread = threading.Thread(target=self.receive_messages)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

if __name__ == "__main__":
    chat_client = ChatClient()
    chat_client.run()
