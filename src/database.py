import sqlite3
import os.path
import threading


class AnkiGenDB:

    lock = threading.Lock()

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
                state               INTEGER)
                ''')
        self.conn.execute(
            '''CREATE TABLE stats (
                id                  INTEGER PRIMARY KEY,
                username            STRING,
                password            STRING,
                deck                STRING,
                language            INTEGER,
                state               INTEGER)
                ''')

        self.conn.commit()

    def get_data(self, id_chat):
        with self.lock:
            query = '''SELECT username, password, deck FROM users
                        WHERE id_chat = ?'''
            ret = self.cur.execute(query, (id_chat,)).fetchone()
            if not ret:
                return None
            else:
                return (ret[0], ret[1], ret[2])

    def get_language(self, id_chat):
        with self.lock:
            query = '''SELECT language FROM users
                        WHERE id_chat=?'''
            ret = self.cur.execute(query, (id_chat,)).fetchone()
            if not ret:
                return None
            else:
                return ret[0]

    def get_state(self, id_chat):
        with self.lock:
            query = '''SELECT state FROM users
                        WHERE id_chat=?'''
            ret = self.cur.execute(query, (id_chat,)).fetchone()
            if not ret:
                return None
            else:
                return ret[0]

    def update_username(self, id_chat, username):
        with self.lock:
            update_query = '''UPDATE users
                              SET username = ?, state = ?
                              WHERE id_chat = ?'''
            self.conn.execute(update_query, (username, -1, id_chat))
            self.conn.commit()

    def update_password(self, id_chat, password):
        with self.lock:
            update_query = '''UPDATE users
                              SET password = ?, state = ?
                              WHERE id_chat = ?'''
            self.conn.execute(update_query, (password, -1, id_chat))
            self.conn.commit()

    def update_deck(self, id_chat, deck):
        with self.lock:
            update_query = '''UPDATE users
                              SET deck= ?, state = ?
                              WHERE id_chat = ?'''
            self.conn.execute(update_query, (deck, -1, id_chat))
            self.conn.commit()

    def update_language(self, id_chat, language):
        with self.lock:
            update_query = '''UPDATE users
                              SET language = ?
                              WHERE id_chat = ?'''
            self.conn.execute(update_query, (language.value, id_chat))
            self.conn.commit()

    def update_state(self, id_chat, state):
        with self.lock:
            update_query = '''UPDATE users
                              SET state = ?
                              WHERE id_chat = ?'''
            self.conn.execute(update_query, (state.value, id_chat))
            self.conn.commit()

    def insert_new_user(self, id_chat, username=None, password=None, deck=None, language=0, state=-1):
        with self.lock:
            insert_new_user = '''INSERT INTO users VALUES (?,?,?,?,?,?)'''
            self.conn.execute(insert_new_user, (id_chat, username, password, deck, language, state))
            self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()
