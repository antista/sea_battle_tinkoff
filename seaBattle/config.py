from collections import defaultdict

SHIPS_COUNT = defaultdict(lambda: (18, 6, 5, 4, 3))
SHIPS_COUNT[2] = (1, 1, 0, 0, 0)
SHIPS_COUNT[3] = (1, 1, 0, 0, 0)
SHIPS_COUNT[4] = (2, 1, 1, 0, 0)
SHIPS_COUNT[5] = (3, 2, 1, 0, 0)
SHIPS_COUNT[6] = (5, 3, 2, 0, 0)
SHIPS_COUNT[7] = (6, 3, 2, 1, 0)
SHIPS_COUNT[8] = (8, 4, 3, 1, 0)
SHIPS_COUNT[9] = (9, 4, 3, 2, 0)
SHIPS_COUNT[10] = (10, 4, 3, 2, 1)
SHIPS_COUNT[11] = (12, 5, 4, 2, 1)
SHIPS_COUNT[12] = (13, 5, 4, 3, 1)
SHIPS_COUNT[13] = (14, 5, 4, 3, 2)
SHIPS_COUNT[14] = (16, 6, 5, 3, 2)

CELL_NEIGHBOURS = ((-1, -1), (0, -1), (1, -1),
                   (-1, 0), (1, 0),
                   (-1, 1), (0, 1), (1, 1))
