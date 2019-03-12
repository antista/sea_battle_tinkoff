import string
import random

from . import strings
from seaBattle.config import get_ships_count, CELL_NEIGHBOURS


class SeaBattle:
    def __init__(self, size):
        self.size = size
        self.map = {x: [' ' for _ in range(self.size)] for x in string.ascii_uppercase[:self.size]}
        self.enemy_map = {x: [' ' for _ in range(self.size)] for x in string.ascii_uppercase[:self.size]}
        self.ships_count = get_ships_count(self.size)
        self.ships_cells = dict()
        self.ships = []
        self.generate_map()
        self.my_turn = True

    def generate_map(self):
        for i in range(1, 5):
            self.generate_ships(i)
        self.delete_marks()
        self.ships_count = self.ships_count[0]

    def delete_marks(self):
        for key in self.map.keys():
            for i in range(len(self.map[key])):
                if self.map[key][i] == '*':
                    self.map[key][i] = ' '

    def mark_neighbour_cells(self, ship):
        for cell in self.ships[ship]:
            for n in CELL_NEIGHBOURS:
                if chr(ord(cell[0]) + n[0]) in self.map.keys() and \
                        len(self.map[chr(ord(cell[0]) + n[0])]) > cell[1] + n[1] >= 0 and \
                        self.map[chr(ord(cell[0]) + n[0])][cell[1] + n[1]] == ' ':
                    self.map[chr(ord(cell[0]) + n[0])][cell[1] + n[1]] = '*'

    def put_cell(self, cell, ship):
        self.map[cell[0]][cell[1]] = 'S'
        self.ships_cells[(cell[0], cell[1])] = ship
        self.ships[ship].append((cell[0], cell[1]))

    def check_horizontal_ship(self, ship_size, cell):
        for i in range(ship_size):
            if cell[1] + i >= len(self.map[cell[0]]) or self.map[cell[0]][cell[1] + i] != ' ':
                return False
        return True

    def check_vertical_ship(self, ship_size, cell):
        for i in range(ship_size):
            if chr(ord(cell[0]) + i) not in self.map.keys() \
                    or self.map[chr(ord(cell[0]) + i)][cell[1]] != ' ':
                return False
        return True

    def generate_ships(self, ship_size):
        for ship in range(self.ships_count[ship_size]):
            self.ships.append([])
            curr_ship = len(self.ships) - 1
            while True:
                cell = (random.choice(list(self.map.keys())), random.randint(0, self.size - 1))
                if self.map[cell[0]][cell[1]] != ' ':
                    continue
                if self.check_horizontal_ship(ship_size, cell):
                    for i in range(ship_size):
                        self.put_cell((cell[0], cell[1] + i), curr_ship)
                elif self.check_vertical_ship(ship_size, cell):
                    for i in range(ship_size):
                        self.put_cell((chr(ord(cell[0]) + i), cell[1]), curr_ship)
                else:
                    continue  # pragma: no cover
                break

            self.mark_neighbour_cells(curr_ship)

    @staticmethod
    def print_map(map):  # pragma: no cover
        print('   |', ' | '.join([str(i + 1) for i in range(len(map))]), '|')
        for key in map.keys():
            print('--' * int(len(map) * 2.5))
            print(key, ' |', ' | '.join(map[key]), ' |')

    def make_enemy_move(self, move):
        def check_hit():
            for ship in self.ships[self.ships_cells[move]]:
                if self.map[ship[0]][ship[1]] != '+':
                    return strings.HIT
            self.ships_count -= 1
            if not self.ships_count:
                return strings.ENEMY_WON
            return strings.KILL

        try:
            move = (move[0].upper(), int(move[1:]) - 1)
            if move[0] not in self.map.keys() or \
                    move[1] > len(self.map[move[0]]):
                raise Exception
        except:
            return strings.WRONG_MOVE
        if self.map[move[0]][move[1]] in '+.':
            return strings.ALREADY_BEEN_HERE
        if self.map[move[0]][move[1]] == ' ':
            self.map[move[0]][move[1]] = '.'
            self.my_turn = True
            return strings.MISSED
        if self.map[move[0]][move[1]] == 'S':
            self.map[move[0]][move[1]] = '+'
            return check_hit()

    def make_move(self, move, move_result):
        if move_result == strings.MISSED:
            self.enemy_map[move[0].upper()][int(move[1:]) - 1] = '.'
            self.my_turn = False
        elif move_result == strings.ALREADY_BEEN_HERE or \
                move_result == strings.WRONG_MOVE:
            pass
        else:
            self.enemy_map[move[0].upper()][int(move[1:]) - 1] = '+'
            self.my_turn = True

    def process_my_move(self, conn):
        move = input('Ваш ход: ')
        conn.send(move.encode())

        if move == 'quit':
            return True

        move_result = conn.recv(1024).decode()

        self.make_move(move, move_result)
        self.print_map(self.enemy_map)
        if move_result == strings.ENEMY_WON:  # pragma: no cover
            print('Вы выиграли')
            return True
        print(move_result)

    def process_enemy_move(self, conn, enemy_number):
        print(f'Ходит игрок {enemy_number}.')

        enemy_move = conn.recv(1024).decode()
        if enemy_move == 'quit' or not enemy_move:  # pragma: no cover
            print(f'Игрок {enemy_number} завершил игру.')
            return True

        print(f'Игрок {enemy_number} сходил на {enemy_move}')

        move_result = self.make_enemy_move(enemy_move)
        self.print_map(self.map)

        conn.send(move_result.encode())

        if move_result == strings.ENEMY_WON:
            print(move_result)
            return True

        print(move_result)
