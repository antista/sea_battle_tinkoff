import string
import random

from . import strings
from seaBattle.config import SHIPS_COUNT, CELL_NEIGHBOURS


class SeaBattle:
    def __init__(self, size):
        self.size = size
        self.map = {x: [' ' for _ in range(self.size)] for x in string.ascii_uppercase[:self.size]}
        self.enemy_map = {x: [' ' for _ in range(self.size)] for x in string.ascii_uppercase[:self.size]}
        self.ships_count = SHIPS_COUNT[self.size]
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
        for line in self.map.values():
            for i, mark in enumerate(line):
                if mark == '*':
                    line[i] = ' '

    def mark_neighbour_cells(self, ship):
        for cell in self.ships[ship]:
            for n in CELL_NEIGHBOURS:
                curr_cell_letter = self.find_another_letter(cell[0], n[0])
                curr_cell_number = cell[1] + n[1]
                if curr_cell_letter in self.map:
                    if len(self.map[curr_cell_letter]) > curr_cell_number >= 0:
                        if self.map[curr_cell_letter][curr_cell_number] == ' ':
                            self.map[curr_cell_letter][curr_cell_number] = '*'

    def put_cell(self, cell, ship):
        self.map[cell[0]][cell[1]] = 'S'
        self.ships_cells[cell] = ship
        self.ships[ship].append(cell)

    def check_horizontal_ship(self, ship_size, cell):
        for i in range(ship_size):
            if cell[1] + i >= len(self.map[cell[0]]) or self.map[cell[0]][cell[1] + i] != ' ':
                return False
        return True

    def check_vertical_ship(self, ship_size, cell):
        for i in range(ship_size):
            if self.find_another_letter(cell[0], i) not in self.map.keys() \
                    or self.map[self.find_another_letter(cell[0], i)][cell[1]] != ' ':
                return False
        return True

    def generate_ships(self, ship_size):
        for ship in range(self.ships_count[ship_size]):
            self.ships.append([])
            curr_ship = len(self.ships) - 1
            while True:
                cell_letter = random.choice(list(self.map.keys()))
                cell_number = random.randint(0, self.size - 1)
                if self.map[cell_letter][cell_number] != ' ':
                    continue
                if self.check_horizontal_ship(ship_size, (cell_letter, cell_number)):
                    for i in range(ship_size):
                        self.put_cell((cell_letter, cell_number + i), curr_ship)
                elif self.check_vertical_ship(ship_size, (cell_letter, cell_number)):
                    for i in range(ship_size):
                        self.put_cell((self.find_another_letter(cell_letter, i), cell_number), curr_ship)
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

    @staticmethod
    def find_another_letter(curr: str, diff: int):
        return chr(ord(curr) + diff)

    def check_hit(self, move):
        for ship in self.ships[self.ships_cells[move]]:
            if self.map[ship[0]][ship[1]] != '+':
                return strings.HIT
        self.ships_count -= 1
        if not self.ships_count:
            return strings.ENEMY_WON
        return strings.KILL

    def make_enemy_move(self, move):
        try:
            cell_letter, cell_number = self.normalize_cell_definition(move)
        except:
            return strings.WRONG_MOVE
        if cell_letter not in self.map.keys() or \
                cell_number > len(self.map[cell_letter]):
            return strings.WRONG_MOVE

        if self.map[cell_letter][cell_number] in '+.':
            return strings.ALREADY_BEEN_HERE
        if self.map[cell_letter][cell_number] == ' ':
            self.map[cell_letter][cell_number] = '.'
            self.my_turn = True
            return strings.MISSED
        if self.map[cell_letter][cell_number] == 'S':
            self.map[cell_letter][cell_number] = '+'
            return self.check_hit((cell_letter, cell_number))
        raise RuntimeError('Undefined cell value')

    def make_move(self, move, move_result):
        cell_letter, cell_number = self.normalize_cell_definition(move)
        if move_result == strings.MISSED:
            self.enemy_map[cell_letter][cell_number] = '.'
            self.my_turn = False
        elif move_result in {strings.ALREADY_BEEN_HERE, strings.WRONG_MOVE}:
            pass
        elif move_result in {strings.HIT, strings.KILL}:
            self.enemy_map[cell_letter][cell_number] = '+'
            self.my_turn = True
        else:
            pass

    def normalize_cell_definition(self, cell):
        return cell[0].upper(), int(cell[1:]) - 1

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
        try:
            move_result = self.make_enemy_move(enemy_move)
        except RuntimeError('Undefined cell value'):  # pragma: no cover
            conn.send('Возникли неполадки')
            print('У игрока неполадки')
            return True
        self.print_map(self.map)

        conn.send(move_result.encode())

        if move_result == strings.ENEMY_WON:
            print(move_result)
            return True

        print(move_result)
