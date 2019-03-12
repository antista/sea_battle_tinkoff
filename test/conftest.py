import pytest

from seaBattle.game import SeaBattle


@pytest.fixture()
def small_game():
    return SeaBattle(3)


@pytest.fixture()
def standart_game():
    return SeaBattle(10)


@pytest.fixture()
def big_game():
    return SeaBattle(25)
