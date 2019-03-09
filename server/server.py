import socket

from connection import connection
from seaBattle.game import SeaBattle


def server():
    def get_field_size():
        while True:
            try:
                size = int(input('Введите ширину поля для игры от 2 до 26: '))
                if size < 2 or size > 26:
                    raise ValueError
                return size
            except ValueError:
                print('Пожалуйста, введите число от 2 до 26.')

    field_size = get_field_size()
    game = SeaBattle(field_size)
    with socket.socket() as s:
        s.bind(connection.get_addres())
        print('Ожидаем подключения второго игрока...')
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            conn.send(str(field_size).encode())
            game.print_map(game.map)
            exit = False
            while not exit:
                while game.my_turn and not exit:
                    exit = game.process_my_move(conn)
                while not game.my_turn and not exit:
                    exit = game.process_enemy_move(conn, 2)
