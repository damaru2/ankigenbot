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
                ipa                 INTEGER DEFAULT 0)
                ''')
        self.conn.execute(
            '''CREATE TABLE deck_names (
                id_chat             INTEGER,
                language            INTEGER,
                deck                STRING,
                PRIMARY KEY(id_chat, language)
            )
                ''')

        self.conn.commit()

    @lock
    def get_data(self, id_chat):
        query = '''SELECT username, password FROM users
                    WHERE id_chat = ?'''
        ret = self.cur.execute(query, (id_chat,)).fetchone()
        if not ret:
            return None
        else:
            return (ret[0], ret[1])

    @lock
    def get_all_deck_names(self, id_chat):
        query = '''SELECT deck, language FROM deck_names
                    WHERE id_chat = ?
                    ORDER BY language ASC'''
        return self.cur.execute(query, (id_chat,)).fetchall()
    @lock
    def get_deck_name(self, id_chat, lang_code):
        query = '''SELECT deck FROM deck_names
                    WHERE id_chat = ? AND language = ?'''
        ret = self.cur.execute(query, (id_chat,int(lang_code))).fetchone()
        if not ret:
            return None
        else:
            return ret[0]
    @lock
    def get_language(self, id_chat):
        query = '''SELECT language FROM users
                    WHERE id_chat=?'''
        ret = self.cur.execute(query, (id_chat,)).fetchone()
        if not ret:
            return None
        else:
            return ret[0]

    @lock
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
    def update_deck_name(self, id_chat, deck, lang):
        insert_or_update_query = '''INSERT OR REPLACE INTO deck_names(id_chat, language, deck)
                           VALUES (?,?,?)
                           '''
        self.conn.execute(insert_or_update_query, (id_chat, lang.value, deck))
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
    def insert_new_user(self, id_chat, username=None, password=None, language=0, state=State.normal.value, reverse=0, ipa=0):
        insert_new_user = '''INSERT INTO users VALUES (?,?,?,?,?,?,?)'''
        self.conn.execute(insert_new_user, (id_chat, username, password, language, state, reverse, ipa))
        self.conn.commit()

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
    pass
    db = AnkiGenDB()
    query = '''SELECT id_chat, username, password, deck, language, state, reverse_order, ipa FROM users'''
    ret = db.cur.execute(query, ()).fetchall()
    db2 = AnkiGenDB('data/data')

    for id_chat, username, password, deck, language, state, reverse_order, ipa in ret:
        insert_new_user = '''INSERT INTO users VALUES (?,?,?,?,?,?,?)'''
        db2.conn.execute(insert_new_user, (id_chat, username, password, language, state, reverse_order, ipa))
        if deck is not None:
            insert_new_deck = '''INSERT INTO deck_names VALUES (?,?,?)'''
            db2.conn.execute(insert_new_deck, (id_chat, language, deck))
    db2.conn.commit()

    #db.conn.execute('''ALTER TABLE users ADD COLUMN ipa INTEGER DEFAULT 0''')
    #db.conn.commit()
