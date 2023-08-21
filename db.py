import sqlite3


class Database: #table name == users
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user_to_users(self, chat_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO 'users' (chat_id) VALUES (?) ", (chat_id,))

    def add_time_to_users(self, chat_id, time_for_attention):
        with self.connection:
            return self.cursor.execute("UPDATE 'users' SET time_for_attention = ? WHERE chat_id = ?", (time_for_attention, chat_id))

    def add_notification_to_notifications(self, chat_id, text, time):
        with self.connection:
            return self.cursor.execute("INSERT INTO 'notifications' (chat_id, text, time) VALUES (?, ?, ?)", (chat_id, text, time))

    def user_exists(self, chat_id):
        with self.connection:
            res = self.cursor.execute("SELECT COUNT(*) FROM 'users' WHERE chat_id = ?", (chat_id,)).fetchall()
            return (res)

    def get_time(self, chat_id):
        with self.connection:
            return self.cursor.execute("SELECT time_for_attention FROM 'users' WHERE chat_id = ?", (chat_id,)).fetchone()[0]

    def get_quantity_notifiactions(self, chat_id) -> int:
        with self.connection:
            return self.cursor.execute("SELECT quantity_of_notification FROM 'users' WHERE chat_id = ?", (chat_id,)).fetchone()[0]

    def get_all_database(self): #DELETE THIS
        with self.connection:
            return self.cursor.execute("SELECT * FROM 'users'")