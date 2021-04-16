from sockets.GameServerSocket import Server

host = 'localhost'
port = 777
server = Server(host, port)
server.start()
