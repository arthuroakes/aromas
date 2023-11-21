# util/Database.py
import sqlite3

class Database:
    @classmethod
    def createConnection(cls):
        conn = sqlite3.connect("dados.db")
        return conn