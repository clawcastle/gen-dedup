import sqlite3
from flask import g


class Database:

    @staticmethod
    def get_db():
        # Connect to the sqlite DB at 'files.db' and store the connection in 'g.db'
        # Re-use the connection if it already exists
        if 'db' not in g:
            g.db = sqlite3.connect('namenode/files.db',
                                   detect_types=sqlite3.PARSE_DECLTYPES)
            # Enable casting Row objects to Python dictionaries
            g.db.row_factory = sqlite3.Row
        return g.db

    @staticmethod
    def close_db(e=None):
        db = g.pop('db', None)

        if db is not None:
            db.close()
