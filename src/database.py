import sqlite3
import os.path
import threading
import functools
import traceback
from enums import *


def lock(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        with AnkiGenDB.lock_db:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print(traceback.format_exc())
                self.conn.commit()
                self.conn.close()
    return wrapper


class AnkiGenDB:

    lock_db = threading.Lock()

    def __init__(self, db_folder='data'):
        db_name = "{}/users.db".format(db_folder)
        create_tables = not os.path.isfile(db_name)
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        if create_tables:
            self.__create_tables()

    def __create_tables(self):
        # id_selected_game is the id_group of the game selected by the user

        self.conn.execute(
            '''CREATE TABLE users (
                id_chat             INTEGER PRIMARY KEY,
                username            STRING,
                password            STRING,
                language            INTEGER,
                state               INTEGER,
                reverse_order       INTEGER DEFAULT 0,
                ipa                 INTEGER DEFAULT 0,
                card_type                 STRING DEFAULT "")
                ''')
        # TODO add columns word_lang def_lang use them. The row should be created if it doesn't exist, even if there was not deck name added.
        self.conn.execute(
            '''CREATE TABLE deck_names (
                id_chat             INTEGER,
                language            INTEGER,
                word_lang           STRING DEFAULT "",
                def_lang            STRING DEFAULT "",
                deck                STRING DEFAULT "",
                tags                STRING DEFAULT "",
                PRIMARY KEY(id_chat, language)
            )
                ''')

        self.conn.commit()

    def get_data(self, id_chat):
        query = '''SELECT username, password, card_type FROM users
                    WHERE id_chat = ?'''
        ret = self.cur.execute(query, (id_chat,)).fetchone()
        if not ret:
            return None
        else:
            return (ret[0], ret[1], ret[2])

    def get_all_deck_names(self, id_chat):
        query = '''SELECT deck, language FROM deck_names
                    WHERE id_chat = ?
                    ORDER BY language ASC'''
        return self.cur.execute(query, (id_chat,)).fetchall()

    def get_all_def_langs(self, id_chat):
        query = '''SELECT def_lang, language FROM deck_names
                    WHERE id_chat = ?
                    ORDER BY language ASC'''
        return self.cur.execute(query, (id_chat,)).fetchall()

    def get_all_word_langs(self, id_chat):
        query = '''SELECT word_lang, language FROM deck_names
                    WHERE id_chat = ?
                    ORDER BY language ASC'''
        return self.cur.execute(query, (id_chat,)).fetchall()

    def get_all_tags(self, id_chat):
        query = '''SELECT tags, language FROM deck_names
                    WHERE id_chat = ?
                    ORDER BY language ASC'''
        return self.cur.execute(query, (id_chat,)).fetchall()

    def get_deck_name(self, id_chat, lang_code):
        query = '''SELECT deck FROM deck_names
                    WHERE id_chat = ? AND language = ?'''
        ret = self.cur.execute(query, (id_chat,int(lang_code))).fetchone()
        if not ret:
            return None
        else:
            return ret[0]

    def get_tags(self, id_chat, lang_code):
        query = '''SELECT tags FROM deck_names
                    WHERE id_chat = ? AND language = ?'''
        ret = self.cur.execute(query, (id_chat,int(lang_code))).fetchone()
        if not ret:
            return None
        else:
            return ret[0]

    def get_word_lang(self, id_chat, lang_code):
        query = '''SELECT word_lang FROM deck_names
                    WHERE id_chat = ? AND language = ?'''
        ret = self.cur.execute(query, (id_chat, int(lang_code))).fetchone()
        if not ret:
            return None
        else:
            return ret[0]

    def get_def_lang(self, id_chat, lang_code):
        query = '''SELECT def_lang FROM deck_names
                    WHERE id_chat = ? AND language = ?'''
        ret = self.cur.execute(query, (id_chat, int(lang_code))).fetchone()
        if not ret:
            return None
        else:
            return ret[0]

    def get_language(self, id_chat):
        query = '''SELECT language FROM users
                    WHERE id_chat=?'''
        ret = self.cur.execute(query, (id_chat,)).fetchone()
        if not ret:
            return None
        else:
            return ret[0]

    def get_state(self, id_chat):
        query = '''SELECT state FROM users
                    WHERE id_chat=?'''
        ret = self.cur.execute(query, (id_chat,)).fetchone()
        if not ret:
            return None
        else:
            return ret[0]

    @lock
    def update_username(self, id_chat, username):
        update_query = '''UPDATE users
                          SET username = ?, state = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (username, State.normal.value, id_chat))
        self.conn.commit()

    @lock
    def update_password(self, id_chat, password):
        update_query = '''UPDATE users
                          SET password = ?, state = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (password, State.normal.value, id_chat))
        self.conn.commit()

    @lock
    def update_card_type(self, id_chat, card_type):
        update_query = '''UPDATE users
                          SET card_type = ?, state = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (card_type, State.normal.value, id_chat))
        self.conn.commit()

    @lock
    def update_deck_name(self, id_chat, deck, lang):
        if self.get_deck_name(id_chat, lang.value) is not None:
            update_query = '''UPDATE deck_names SET deck = ? WHERE id_chat = ? and language = ?'''
            self.conn.execute(update_query, (deck, id_chat, lang.value))
        else:
            insert_or_update_query = '''INSERT OR REPLACE INTO deck_names(id_chat, language, deck) VALUES (?,?,?)'''
            self.conn.execute(insert_or_update_query, (id_chat, lang.value, deck))
        update_query = '''UPDATE users SET state = ? WHERE id_chat = ?'''
        self.conn.execute(update_query, (State.normal.value, id_chat))
        self.conn.commit()

    @lock
    def update_word_lang(self, id_chat, lang, word_lang):
        # One could check if the whole row is empty (except for the primary keys) and delete the row in case of (not word_lang)
        if self.get_deck_name(id_chat, lang.value) is not None:
            update_query = '''UPDATE deck_names SET word_lang = ? WHERE id_chat = ? and language = ?'''
            self.conn.execute(update_query, (word_lang if word_lang else "", id_chat, lang.value))
        else:
            insert_or_update_query = '''INSERT OR REPLACE INTO deck_names(id_chat, language, word_lang) VALUES (?,?,?)'''
            self.conn.execute(insert_or_update_query, (id_chat, lang.value, word_lang))
        self.conn.commit()

    @lock
    def update_def_lang(self, id_chat, lang, def_lang):
        '''
        :param lang: Language
        :param def_lang: language code from translate shell
        '''
        # One could check if the whole row is empty (except for the primary keys) and delete the row in case of (not def_lang)
        if self.get_deck_name(id_chat, lang.value) is not None:
            update_query = '''UPDATE deck_names SET def_lang = ? WHERE id_chat = ? and language = ?'''
            self.conn.execute(update_query, (def_lang if def_lang else "", id_chat, lang.value))
        else:
            insert_or_update_query = '''INSERT OR REPLACE INTO deck_names(id_chat, language, def_lang) VALUES (?,?,?)'''
            self.conn.execute(insert_or_update_query, (id_chat, lang.value, def_lang))
        self.conn.commit()

    def remove_def_lang(self, id_chat, from_lang):
        # I will not delete the row if it gets empty, for now...
        update_query = '''UPDATE deck_names
                          SET def_lang = ""
                          WHERE id_chat = ? AND language = ?'''
        self.conn.execute(update_query, (id_chat, from_lang.value))
        self.conn.commit()

    def remove_word_lang(self, id_chat, from_lang):
        delete_query = '''UPDATE deck_names
                          SET word_lang = ""
                          WHERE id_chat = ? AND language = ?'''
        self.conn.execute(delete_query, (id_chat, from_lang.value))
        self.conn.commit()

    @lock
    def update_tags(self, id_chat, tags, lang):
        if self.get_tags(id_chat, lang.value) is not None:
            update_query = '''UPDATE deck_names SET tags = ? WHERE id_chat = ? and language = ?'''
            self.conn.execute(update_query, (tags, id_chat, lang.value))
        else:
            insert_or_update_query = '''INSERT OR REPLACE INTO deck_names(id_chat, language, tags) VALUES (?,?,?)'''
            self.conn.execute(insert_or_update_query, (id_chat, lang.value, tags))
        update_query = '''UPDATE users SET state = ? WHERE id_chat = ?'''
        self.conn.execute(update_query, (State.normal.value, id_chat))
        self.conn.commit()

    @lock
    def update_language(self, id_chat, language):
        update_query = '''UPDATE users
                          SET language = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (language, id_chat))
        self.conn.commit()

    @lock
    def update_state(self, id_chat, state):
        update_query = '''UPDATE users
                          SET state = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (state.value, id_chat))
        self.conn.commit()

    @lock
    def insert_new_user(self, id_chat, username=None, password=None, language=0, state=State.normal.value, reverse=0, ipa=0, card_type=''):
        insert_new_user = '''INSERT INTO users VALUES (?,?,?,?,?,?,?,?)'''
        self.conn.execute(insert_new_user, (id_chat, username, password, language, state, reverse, ipa, card_type))
        self.conn.commit()

    @lock
    def reverse_order(self, id_chat):
        rev = self.is_order_reversed(id_chat)
        if rev is None:
            return None
        else:
            rev = 1-rev
        update_query = '''UPDATE users
                          SET reverse_order = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (rev, id_chat))
        self.conn.commit()
        return rev

    @lock
    def swap_ipa(self, id_chat):
        rev = self.get_if_add_phonetics(id_chat)
        if rev is None:
            return None
        else:
            rev = 1-rev
        update_query = '''UPDATE users
                          SET ipa = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (rev, id_chat))
        self.conn.commit()
        return rev


    def is_order_reversed(self, id_chat):
        query = '''SELECT reverse_order FROM users
                    WHERE id_chat = ?'''
        rev = self.cur.execute(query, (id_chat,)).fetchone()
        if rev is None:
            return None
        else:
            return rev[0]

    def get_if_add_phonetics(self, id_chat):
        query = '''SELECT ipa FROM users
                    WHERE id_chat = ?'''
        rev = self.cur.execute(query, (id_chat,)).fetchone()
        if rev is None:
            return None
        else:
            return rev[0]


if __name__ == "__main__":
    db = AnkiGenDB()
    db.conn.execute('''ALTER TABLE deck_names ADD COLUMN word_lang STRING DEFAULT ""''')
    db.conn.execute('''ALTER TABLE deck_names ADD COLUMN def_lang STRING DEFAULT ""''')
    db.conn.commit()
    exit(0)

    #pass
    #db = AnkiGenDB()
    #query = '''SELECT id_chat, username, password, deck, language, state, reverse_order, ipa FROM users'''
    #ret = db.cur.execute(query, ()).fetchall()
    #db2 = AnkiGenDB('data/data')

    #for id_chat, username, password, deck, language, state, reverse_order, ipa in ret:
    #    insert_new_user = '''INSERT INTO users VALUES (?,?,?,?,?,?,?)'''
    #    db2.conn.execute(insert_new_user, (id_chat, username, password, language, state, reverse_order, ipa))
    #    if deck is not None:
    #        insert_new_deck = '''INSERT INTO deck_names VALUES (?,?,?)'''
    #        db2.conn.execute(insert_new_deck, (id_chat, language, deck))
    #db2.conn.commit()

