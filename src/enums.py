from enum import Enum


class Languages(Enum):
    English = 0
    Español = 1
    Français = 2
    Deutsch = 3
    Italiano = 4


class State(Enum):
    normal = -1
    set_user = 0
    set_pass = 1
    set_deck_en = 2
    set_deck_es = 3
    set_deck_fr = 4
    set_deck_de = 5
    set_deck_it = 6

dict_state_to_lang =  {
    State.set_deck_en: Languages.English,
    State.set_deck_es: Languages.Español,
    State.set_deck_fr: Languages.Français,
    State.set_deck_de: Languages.Deutsch,
    State.set_deck_it: Languages.Italiano,
    }
