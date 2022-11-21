import sqlite3
from results import User

connection = sqlite3.connect('users.db')
cursor = connection.cursor()
# cursor.execute("DROP TABLE IF EXISTS Users")
cursor.execute('''CREATE TABLE IF NOT EXISTS Users
              (ID INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT(30), login TEXT(15) UNIQUE, hash TEXT);''')


class DBInteractor:
    @staticmethod
    def insert_user(user: User):
        try:
            statement = 'INSERT INTO Users (name, login, hash) VALUES ("{0}", "{1}", "{2}");'.format(user.name,
                                                                                                     user.login,
                                                                                                     user.hash)
            cursor.execute(statement)
            connection.commit()
            # connection.close()  # !!!!!!!
        except (sqlite3.Error, sqlite3.Warning) as err:
            print(err, "DB PROBLEM")
            return False
        return True

    @staticmethod
    def select_user(user: User):
        try:
            # statement = 'SELECT ID FROM Users WHERE login = "{0}" AND hash = "{1}";'.format(user.login, user.hash)
            statement = 'SELECT ID, hash FROM Users WHERE login = "{0}";'.format(user.login)
            cursor.execute(statement)
            result = cursor.fetchall()
            connection.commit()
            # connection.close()
            if result is None or len(result) == 0:
                return None
        except (sqlite3.Error, sqlite3.Warning) as err:
            print(err, "DB PROBLEM")
            return None
        return result[0]

    @staticmethod
    def find_by_id(idf: str):
        try:
            statement = 'SELECT * FROM Users WHERE ID = "{0}";'.format(idf)
            cursor.execute(statement)
            result = cursor.fetchall()
            connection.commit()
            # connection.close()
            if result is None or len(result) == 0:
                return None
        except (sqlite3.Error, sqlite3.Warning) as err:
            print(err, "DB PROBLEM")
            return None
        return result[0]
