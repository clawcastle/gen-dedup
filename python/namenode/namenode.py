from .database import Database
import json

database = Database()


def save_metadata(filename, size, content_type, blocks):
    # Insert the File record in the DB
    db = database.get_db()
    cursor = db.execute(
        "INSERT INTO `file`(`filename`, `size`, `content_type`, `storage_blocks`) VALUES (?,?,?,?)",
        (filename, size, content_type, json.dumps(blocks))
    )
    db.commit()


def get_metadata(filename):
    db = Database.get_db()
    cursor = db.execute("SELECT * FROM `file` WHERE `filename`=?", [filename])
    if not cursor:
        raise Exception('Error connecting to the database')
    data = cursor.fetchone()

    if not data:
        raise Exception('File not found')

    file_metadata = dict(data)

    return file_metadata['size'], file_metadata['content_type'], json.loads(file_metadata['storage_blocks'])
