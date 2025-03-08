# online-chat-messenger &middot; ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

複数ユーザによるチャット/ルームチャットを簡易的に実装しています。
TCP/UDPおよびカスタムプロトコルを活用したプロセス間通信を行います。

## Usage

### Standard Chat

サーバとクライアントがUDPネットワークソケットを使用してメッセージのやり取りをします。

サーバにはリレーシステムが組み込まれており、現在接続中のすべてのクライアントの情報を一時的にメモリ上に保存します。新しいメッセージがサーバに届くと、そのメッセージは現在接続中の全クライアントにリレーされます。

```:python
$ python standard_chat/server.py
[SERVER] Server is listening...
```

```:python
$ python standard_chat/client.py
Enter your username: user1
[CLIENT] Connected to the server.
> hello!
> [user2] hi!
```

```:python
$ python standard_chat/client.py
Enter your username: user2
[CLIENT] Connected to the server.
> hi!
```

### Room Chat

サーバとクライアントがTCP、UDPネットワークソケットを使用してメッセージのやり取りをします。

ユーザはチャットルームで他ユーザ（ルーム参加者）とチャットを行います。
新しいチャットルームを作成するプロセスや既存のチャットルームに参加するためにTCP接続を、チャットルーム内でのメッセージのやり取りにUDP接続を用います。

```:python
$ python room_chat/server.py
server is listening...
```

```:python
$ python room_chat/client.py
connected to the server

do you want to create chat room or join chat room? input 'create' or 'join' > create
input room name you want to create or join > room1
input password of room > password
input maximum number of participants > 5
> hello!!!
> [127.0.0.1:54455@room1] hi!
> welcome!
```

```:python
$ python room_chat/client.py
connected to the server

do you want to create chat room or join chat room? input 'create' or 'join' > join
input room name you want to create or join > room1
input password of room > password
> hi!
> [127.0.0.1:54457@room1] welcome!
```
