from enum import Enum


class Languages(Enum):
    en = 0
    es = 1
    fr = 2
    de = 3
    it = 4


class State(Enum):
    normal = -1
    set_user = 0
    set_pass = 1
    set_deck = 2
