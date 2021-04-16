import re
import socket

import select


class Player:
    host = 'localhost'
    port = 777
    sock = socket.socket()
    sock.connect((host, port))
    while True:
        r, w, e = select.select([sock], [], [], 1)
        for s in r:
            if s == sock:
                n = s.recv(1024)
                if n == b"enter command":
                    sock.send(bytes(input("Enter command\n"), encoding="utf8"))
                elif re.match("total .+", n.decode("utf8")):
                    print(n.decode("utf8"))
                    exit(0)
                else:
                    print(n.decode("utf8"))
