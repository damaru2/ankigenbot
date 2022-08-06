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
    setting_defi_lang_en = 17
    setting_defi_lang_es = 18
    setting_defi_lang_fr = 19
    setting_defi_lang_de = 20
    setting_defi_lang_it = 21
    setting_defi_lang_ja = 22
    setting_defi_lang_ru = 23
    setting_word_lang_en = 24
    setting_word_lang_es = 25
    setting_word_lang_fr = 26
    setting_word_lang_de = 27
    setting_word_lang_it = 28
    setting_word_lang_ja = 29
    setting_word_lang_ru = 30


dict_state_to_lang = {
    State.set_deck_en: Languages.English,
    State.set_deck_es: Languages.Español,
    State.set_deck_fr: Languages.Français,
    State.set_deck_de: Languages.Deutsch,
    State.set_deck_it: Languages.Italiano,
    #State.set_deck_ja: Languages.Japanese,
    State.set_deck_ru: Languages.Russian,
    }


dict_state_to_lang_tags = {
    State.set_tags_en: Languages.English,
    State.set_tags_es: Languages.Español,
    State.set_tags_fr: Languages.Français,
    State.set_tags_de: Languages.Deutsch,
    State.set_tags_it: Languages.Italiano,
    #State.set_tags_ja: Languages.Japanese,
    State.set_tags_ru: Languages.Russian,
}

dict_state_to_lang_defi = {
    State.setting_defi_lang_en: Languages.English,
    State.setting_defi_lang_es: Languages.Español,
    State.setting_defi_lang_fr: Languages.Français,
    State.setting_defi_lang_de: Languages.Deutsch,
    State.setting_defi_lang_it: Languages.Italiano,
    State.setting_defi_lang_ja: Languages.Japanese,
    State.setting_defi_lang_ru: Languages.Russian,
}

dict_state_to_lang_word = {
    State.setting_word_lang_en: Languages.English,
    State.setting_word_lang_es: Languages.Español,
    State.setting_word_lang_fr: Languages.Français,
    State.setting_word_lang_de: Languages.Deutsch,
    State.setting_word_lang_it: Languages.Italiano,
    State.setting_word_lang_ja: Languages.Japanese,
    State.setting_word_lang_ru: Languages.Russian,
}


supported_language_codes = {
    "af": "Afrikaans",
    "am": "Amharic",
    "ar": "Arabic",
    "az": "Azerbaijani",
    "ba": "Bashkir",
    "be": "Belarusian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "ceb": "Cebuano",
    "co": "Corsican",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "eo": "Esperanto",
    "es": "Spanish",
    "et": "Estonian",
    "eu": "Basque",
    "fa": "Persian",
    "fi": "Finnish",
    "fj": "Fijian",
    "fr": "French",
    "fy": "Frisian",
    "ga": "Irish",
    "gd": "Scots Gaelic",
    "gl": "Galician",
    "gu": "Gujarati",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "he": "Hebrew",
    "hi": "Hindi",
    "hmn": "Hmong",
    "hr": "Croatian",
    "ht": "Haitian Creole",
    "hu": "Hungarian",
    "hy": "Armenian",
    "id": "Indonesian",
    "ig": "Igbo",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "jv": "Javanese",
    "ka": "Georgian",
    "kk": "Kazakh",
    "km": "Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "ku": "Kurdish",
    "ky": "Kyrgyz",
    "la": "Latin",
    "lb": "Luxembourgish",
    "lo": "Lao",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mg": "Malagasy",
    "mhr": "Eastern Mari",
    "mi": "Maori",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mn": "Mongolian",
    "mr": "Marathi",
    "mrj": "Hill Mari",
    "ms": "Malay",
    "mt": "Maltese",
    "mww": "Hmong Daw",
    "my": "Myanmar",
    "ne": "Nepali",
    "nl": "Dutch",
    "no": "Norwegian",
    "ny": "Chichewa",
    "or": "Oriya",
    "otq": "Querétaro Otomi",
    "pa": "Punjabi",
    "pap": "Papiamento",
    "pl": "Polish",
    "ps": "Pashto",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "rw": "Kinyarwanda",
    "sd": "Sindhi",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sm": "Samoan",
    "sn": "Shona",
    "so": "Somali",
    "sq": "Albanian",
    "sr": "Serbian",
    "st": "Sesotho",
    "su": "Sundanese",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "tg": "Tajik",
    "th": "Thai",
    "tk": "Turkmen",
    "tl": "Filipino",
    "tlh": "Klingon",
    "tlh-Qaak": "Klingon (pIqaD)",
    "to": "Tongan",
    "tr": "Turkish",
    "tt": "Tatar",
    "ty": "Tahitian",
    "udm": "Udmurt",
    "ug": "Uyghur",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "vi": "Vietnamese",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "yo": "Yoruba",
    "yua": "Yucatec Maya",
    "yue": "Cantonese",
    "zh-CN": "Chinese Simplified",
    "zh-TW": "Chinese Traditional",
    "zu": "Zulu",
}
