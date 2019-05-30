import sqlite3
import os.path
import threading
import functools
import traceback


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
                deck                STRING,
                language            INTEGER,
                state               INTEGER,
                reverse_order       INTEGER DEFAULT 0,
                ipa                 INTEGER DEFAULT 0)
                ''')

        self.conn.commit()

    @lock
    def get_data(self, id_chat):
        query = '''SELECT username, password, deck FROM users
                    WHERE id_chat = ?'''
        ret = self.cur.execute(query, (id_chat,)).fetchone()
        if not ret:
            return None
        else:
            return (ret[0], ret[1], ret[2])

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
        self.conn.execute(update_query, (username, -1, id_chat))
        self.conn.commit()

    @lock
    def update_password(self, id_chat, password):
        update_query = '''UPDATE users
                          SET password = ?, state = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (password, -1, id_chat))
        self.conn.commit()

    @lock
    def update_deck(self, id_chat, deck):
        update_query = '''UPDATE users
                          SET deck= ?, state = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (deck, -1, id_chat))
        self.conn.commit()

    @lock
    def update_language(self, id_chat, language):
        update_query = '''UPDATE users
                          SET language = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (language.value, id_chat))
        self.conn.commit()

    @lock
    def update_state(self, id_chat, state):
        update_query = '''UPDATE users
                          SET state = ?
                          WHERE id_chat = ?'''
        self.conn.execute(update_query, (state.value, id_chat))
        self.conn.commit()

    @lock
    def insert_new_user(self, id_chat, username=None, password=None, deck=None, language=0, state=-1, reverse=0, ipa=0):
        insert_new_user = '''INSERT INTO users VALUES (?,?,?,?,?,?,?,?)'''
        self.conn.execute(insert_new_user, (id_chat, username, password, deck, language, state, reverse, ipa))
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
    #db = AnkiGenDB()
    #db.conn.execute('''ALTER TABLE users ADD COLUMN ipa INTEGER DEFAULT 0''')
    #db.conn.commit()
