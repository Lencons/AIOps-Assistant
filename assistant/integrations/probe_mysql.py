import mysql.connector

class MySQL:

    def __init__(self, user, password, host, database):

        # record our connection information
        self.user = user
        self.password = password
        self.host = host
        self.database = database

        self.db_conn = mysql.connector.connect(
            user = self.user,
            password = self.password,
            host = self.host,
            database = self.database
        )

    def ping_db(self):
        return True