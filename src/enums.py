from enum import Enum


class Languages(Enum):
    English = 0
    Español = 1
    Français = 2
    Deutsch = 3
    Italiano = 4
    Japanese = 5
    Russian = 6


class State(Enum):
    normal = -1
    set_user = 0
    set_pass = 1
    set_deck_en = 2
    set_deck_es = 3
    set_deck_fr = 4
    set_deck_de = 5
    set_deck_it = 6
    set_deck_ja = 7
    set_deck_ru = 8
    set_card_type = 9
    set_tags_en = 10
    set_tags_es = 11
    set_tags_fr = 12
    set_tags_de = 13
    set_tags_it = 14
    set_tags_ja = 15
    set_tags_ru = 16


dict_state_to_lang =  {
    State.set_deck_en: Languages.English,
    State.set_deck_es: Languages.Español,
    State.set_deck_fr: Languages.Français,
    State.set_deck_de: Languages.Deutsch,
    State.set_deck_it: Languages.Italiano,
    #State.set_deck_ja: Languages.Japanese,
    State.set_deck_ru: Languages.Russian,
    }

dict_state_to_lang_tags =  {
    State.set_tags_en: Languages.English,
    State.set_tags_es: Languages.Español,
    State.set_tags_fr: Languages.Français,
    State.set_tags_de: Languages.Deutsch,
    State.set_tags_it: Languages.Italiano,
    #State.set_tags_ja: Languages.Japanese,
    State.set_tags_ru: Languages.Russian,
}
