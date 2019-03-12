from seaBattle import config, strings
from seaBattle.game import SeaBattle


def test_init(mocker, small_game, standart_game, big_game):
    mocker.patch('seaBattle.game.SeaBattle.generate_map')
    game = SeaBattle(10)
    game.generate_map.assert_called_once()
    assert len(small_game.map) == len(small_game.enemy_map) == 3
    assert len(standart_game.map) == len(standart_game.enemy_map) == 10
    assert len(game.map) == len(game.enemy_map) == 10
    assert len(big_game.map) == len(big_game.enemy_map) == 25


def test_generate_map(mocker, standart_game):
    mocker.patch('seaBattle.game.SeaBattle.generate_ships')
    mocker.patch('seaBattle.game.SeaBattle.delete_marks')
    standart_game.ships_count = config.get_ships_count(10)
    standart_game.generate_map()
    SeaBattle.generate_ships.assert_called_with(4)
    SeaBattle.delete_marks.assert_called_once()


def test_generate_ships_standart(mocker, standart_game):
    mocker.patch('seaBattle.game.SeaBattle.check_horizontal_ship', return_value=True)
    mocker.patch('seaBattle.game.SeaBattle.check_vertical_ship', return_value=True)
    mocker.patch('seaBattle.game.SeaBattle.put_cell')
    mocker.patch('seaBattle.game.SeaBattle.mark_neighbour_cells')
    standart_game.ships_count = config.get_ships_count(10)
    standart_game.generate_ships(4)
    SeaBattle.check_horizontal_ship.assert_called_once()
    SeaBattle.check_vertical_ship.assert_not_called()
    SeaBattle.put_cell.assert_called()
    SeaBattle.mark_neighbour_cells.assert_called_once()


def test_generate_ships_small(mocker, small_game):
    mocker.patch('seaBattle.game.SeaBattle.check_horizontal_ship')
    mocker.patch('seaBattle.game.SeaBattle.check_vertical_ship')
    mocker.patch('seaBattle.game.SeaBattle.put_cell')
    small_game.ships_count = config.get_ships_count(3)
    small_game.generate_ships(4)
    SeaBattle.check_horizontal_ship.assert_not_called()
    SeaBattle.check_vertical_ship.assert_not_called()
    SeaBattle.put_cell.assert_not_called()


def test_put_cell(mocker, small_game):
    mocker.patch('random.choice', return_value='A')
    mocker.patch('random.randint', return_value=2)
    small_game.ships_count = config.get_ships_count(3)
    small_game.generate_ships(1)
    assert small_game.map['A'][2] == 'S'
    assert small_game.ships_cells[('A', 2)] == 1
    assert small_game.ships[1] == [('A', 2)]


def test_check_ship_true(mocker):
    mocker.patch('seaBattle.game.SeaBattle.generate_map')
    game = SeaBattle(10)
    assert game.check_horizontal_ship(4, ('A', 1))
    assert game.check_vertical_ship(4, ('A', 1))


def test_check_ship_false(small_game):
    assert not small_game.check_horizontal_ship(4, ('A', 1))
    assert not small_game.check_vertical_ship(4, ('A', 1))


def test_delete_marks(mocker):
    mocker.patch('seaBattle.game.SeaBattle.generate_map')
    import string
    game = SeaBattle(10)
    game.map = {x: ['*' for _ in range(game.size)] for x in
                string.ascii_uppercase[:game.size]}
    game.delete_marks()
    assert game.map == {x: [' ' for _ in range(game.size)] for x in
                        string.ascii_uppercase[:game.size]}


def test_mark_neighbour_cells(mocker):
    mocker.patch('seaBattle.game.SeaBattle.generate_map')
    game = SeaBattle(10)
    game.ships.append([('A', 1), ('A', 2)])
    game.map['A'][1] = 'S'
    game.map['A'][2] = 'S'
    game.mark_neighbour_cells(0)
    assert game.map['B'][1] == '*'
    assert game.map['C'][1] != '*'
    assert game.map['A'][3] == '*'
    assert game.map['A'][1] != '*'
    assert game.map['A'][0] == '*'


def test_make_enemy_move(mocker):
    mocker.patch('seaBattle.game.SeaBattle.generate_map')
    game = SeaBattle(3)
    game.ships_count = 2
    game.map = {'A': ['+', 'S', '.'],
                'B': [' ', ' ', '.'],
                'C': ['S', 'S', ' ']}
    game.ships.append([('A', 0), ('A', 1)])
    game.ships_cells[('A', 0)] = 0
    game.ships_cells[('A', 1)] = 0
    game.ships.append([('C', 0), ('C', 1)])
    game.ships_cells[('C', 0)] = 1
    game.ships_cells[('C', 1)] = 1
    assert game.make_enemy_move('a1') == strings.ALREADY_BEEN_HERE
    assert game.make_enemy_move('a3') == strings.ALREADY_BEEN_HERE
    assert game.make_enemy_move('B2') == strings.MISSED
    assert game.make_enemy_move('B2') == strings.ALREADY_BEEN_HERE
    assert game.make_enemy_move('h2') == strings.WRONG_MOVE
    assert game.make_enemy_move('A10') == strings.WRONG_MOVE
    assert game.make_enemy_move('A2') == strings.KILL
    assert game.make_enemy_move('C2') == strings.HIT
    assert game.make_enemy_move('C1') == strings.ENEMY_WON


def test_make_move():
    game = SeaBattle(10)
    game.make_move('a1', strings.MISSED)
    assert game.enemy_map['A'][0] == '.'
    assert not game.my_turn
    game.make_move('a1', strings.ALREADY_BEEN_HERE)
    assert not game.my_turn
    game.make_move('a1', strings.WRONG_MOVE)
    assert not game.my_turn
    game.make_move('a5', strings.HIT)
    assert game.enemy_map['A'][4] == '+'
    assert game.my_turn
    game.make_move('a6', strings.KILL)
    assert game.enemy_map['A'][5] == '+'
    assert game.my_turn
    game.make_move('a7', strings.ENEMY_WON)
    assert game.enemy_map['A'][6] == '+'
    assert game.my_turn


def test_process_my_move(mocker):
    mocker.patch('seaBattle.game.SeaBattle.make_move')
    mocker.patch('seaBattle.game.SeaBattle.print_map')
    mocker.patch('builtins.input', return_value='a1')
    mocker.patch('socket.socket.send')
    mocker.patch('socket.socket.recv', result_value=strings.MISSED)
    game = SeaBattle(3)
    import socket
    assert game.process_my_move(socket.socket()) is None
    game.make_move.assert_called_once()
    game.print_map.assert_called_with(game.enemy_map)
    mocker.patch('builtins.input', return_value='quit')
    assert game.process_my_move(socket.socket())


def test_process_enemy_move(mocker):
    mocker.patch('socket.socket.send')
    mocker.patch('socket.socket.recv', result_value='a1')
    mocker.patch('seaBattle.game.SeaBattle.print_map')
    mocker.patch('seaBattle.game.SeaBattle.make_enemy_move', return_value=strings.MISSED)
    game = SeaBattle(3)
    import socket
    assert game.process_enemy_move(socket.socket(), 2) is None
    game.make_enemy_move.assert_called_once()
    game.print_map.assert_called_with(game.map)
    mocker.patch('seaBattle.game.SeaBattle.make_enemy_move', return_value=strings.ENEMY_WON)
    assert game.process_enemy_move(socket.socket(), 2)
