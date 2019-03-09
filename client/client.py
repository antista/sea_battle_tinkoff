import socket

from connection import connection
from seaBattle.game import SeaBattle


def client():
    with socket.socket() as s:
        s.connect(connection.get_addres())
        field_size = s.recv(1024).decode()
        game = SeaBattle(int(field_size))
        game.my_turn = False
        game.print_map(game.map)
        exit = False
        while not exit:
            while game.my_turn and not exit:
                exit = game.process_my_move(s)
            while not game.my_turn and not exit:
                exit = game.process_enemy_move(s, 1)
