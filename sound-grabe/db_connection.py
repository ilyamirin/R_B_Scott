import sqlite3
from peewee import SqliteDatabase

sqlite_db = SqliteDatabase(':memory:', pragmas={'journal_mode': 'wal'})
