import re
import socket
import time
from errno import EINVAL

import select

from models.models import Husband, Wife, House


class Server:
    player1, player2, addr1, addr2 = None, None, None, None
    sockets = []
    w_has_move = False
    h_has_move = False

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.day = 0
        self.socket = socket.socket()
        self.husband = Husband()
        self.house = House()
        self.husband.house = self.house
        self.wife = Wife()
        self.wife.house = self.house

    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(2)
        print("Ожидание подключения игроков")
        self.player1, self.addr1 = self.socket.accept()
        self.player1.send(b"Successfully connected, you are playing as wife")  # русские символы в byte не лезут
        self.player2, self.addr2 = self.socket.accept()
        self.player2.send(b"Successfully connected, you are playing as husband")
        time.sleep(0.05)
        self.send_both_players(b'Game started, enjoy.\n Type "help" for list of commands')
        time.sleep(0.05)  # Для того чтобы не было соединения строк
        self.h_has_move = True
        self.w_has_move = True
        # while (not self.is_finished()) and self.day < 365:
        #     self.sockets = [self.player1, self.player2]
        #
        #     if self.h_has_move and self.w_has_move:
        #         self.send_both_players(b"enter command")
        #     readable, writable, exceptional = select.select(self.sockets, [], [])
        #
        #     for s in readable:
        #         if s is self.player1 and self.w_has_move:
        #             try:
        #                 self.process_wife_message(s.recv(1024))
        #             except IOError as e:
        #                 s.send(bytes(str(e), encoding="utf8"))
        #         elif self.h_has_move:
        #             try:
        #                 self.process_husband_message(s.recv(1024))
        #             except IOError as e:
        #                 s.send(bytes(str(e), encoding="utf8"))
        #     if (not self.h_has_move) and (not self.w_has_move):
        #         self.day += 1
        #         self.h_has_move = True
        #         self.w_has_move = True
        for day in range(1, 366):
            self.day = day
            self.w_has_move = True
            self.h_has_move = True
            self.send_both_players(b"enter command")
            while self.h_has_move or self.w_has_move:
                r, w, e = select.select([self.player1, self.player2], [], [], 2)
                for s in r:
                    if s == self.player1 and self.w_has_move:
                        try:
                            self.process_wife_message(s.recv(1024))
                        except IOError as e:
                            s.send(bytes(str(e), encoding="utf8"))
                            time.sleep(0.05)
                            s.send(b'enter command')
                    elif self.h_has_move:
                        try:
                            self.process_husband_message(s.recv(1024))
                        except IOError as e:
                            s.send(bytes(str(e), encoding="utf8"))
                            time.sleep(0.05)
                            s.send(b'enter command')
            self.house.dirt += 5
            if self.house.dirt > 90:
                self.husband.happiness -= 10
                self.wife.happiness -= 10
            if self.is_finished():
                break
        self.send_both_players(bytes(f"total earned: {self.house.total_money_earned},\n" +
                                     f"total coats: {self.house.total_coats_bought},\n" +
                                     f"total eaten: {self.house.total_food_eaten}",
                                     encoding="utf8"))


    def is_finished(self):
        return (not self.husband.health_status_is_ok()) or (not self.wife.health_status_is_ok())

    def send_both_players(self, message: bytes):
        self.player2.send(message)
        self.player1.send(message)

    def current_status_message(self):
        return bytes(f"House status: [{self.house}]\n" +
                     f"Wife: {self.wife}\n" +
                     f"Husband: {self.husband}\n" +
                     f"day:{self.day}\n" +
                     f"send 'help' for commands list", encoding="utf8")

    def process_wife_message(self, message: bytes):
        message = message.decode("utf8")
        if re.match("eat .+", message):
            try:
                potential_number = re.split(" ", message)[1]
                potential_number = int(potential_number)
                self.wife.eat(potential_number)
                self.w_has_move = False
            except TypeError as e:
                raise IOError("Wrong command. Try again")
        elif re.match("status", message):
            self.player1.send(self.current_status_message())
            raise IOError("Now enter command")
        elif re.match("buy coat", message):
            self.wife.buy_coat()
            self.w_has_move = False
        elif re.match("buy food .+", message):
            try:
                potential_number = re.split(" ", message)[2]
                potential_number = int(potential_number)
                self.wife.buy_food(potential_number)
                self.w_has_move = False
            except TypeError as e:
                raise IOError("Wrong command. Try again")
        elif re.match("clean", message):
            self.wife.clean()
            self.w_has_move = False
        elif re.match("help", message):
            self.player1.send(self.commands_list_wife())
            raise IOError("Now enter command")

        else:
            raise IOError("Incorrect command")

    def process_husband_message(self, message: bytes):
        message = message.decode("utf8")
        if re.match("eat .+", message):
            try:
                potential_number = re.split(" ", message)[1]
                potential_number = int(potential_number)
                self.husband.eat(potential_number)
                self.h_has_move = False
            except TypeError as e:
                raise IOError("Wrong command. Try again")
        elif re.match("status", message):
            self.player2.send(self.current_status_message())
            raise IOError("Now enter command")
        elif re.match("play", message):
            self.husband.play_wot()
            self.h_has_move = False
        elif re.match("work", message):
            self.husband.go_to_work()
            self.h_has_move = False
        elif re.match("help", message):
            self.player2.send(self.commands_list_husband())
            raise IOError("Now enter command")
        else:
            raise IOError("Incorrect command")

    def commands_list_wife(self):
        return b'eat <int> -- eat something. Parameter for amount. Raises satiety by <int>\n' \
               b'buy food <int> -- buy food. Parameter for amount, must be divisible by 10.\n' \
               b'buy coat -- buy coat. Costs 350. Raises happiness by 60\n' \
               b'clean -- clean house. Drops 100 points of dirtiness'

    def commands_list_husband(self):
        return b'eat <int> -- eat something. Parameter for amount\n' \
               b'work -- go to work. Adds 150 to money.\n' \
               b'play -- play WOT. Adds 20 to happiness'
