from database import Database
import json

database = Database()

def get_block_storage_node(block_id):
    db = database.get_db()
    cursor = db.execute(
        "SELECT * FROM `blocks` WHERE `id`=?", [block_id]
    )
    if not cursor:
        raise Exception('Error connecting to the database')
    data = cursor.fetchone()

    if not data:
        return None

    block_data = dict(data)

    return block_data["storage_node"]

def save_block_node_association(block_id, node_id):
    db = database.get_db()
    cursor = db.execute(
        "INSERT INTO `blocks`(`id`, `storage_node`) VALUES (?,?)",
        (block_id, node_id)
    )
    db.commit()

def save_metadata(filename, size, content_type, blocks, strategy):
    # Insert the File record in the DB
    db = database.get_db()
    cursor = db.execute(
        "INSERT INTO `file`(`filename`, `size`, `content_type`, `storage_blocks`, `strategy`) VALUES (?,?,?,?,?)",
        (filename, size, content_type, json.dumps(blocks), strategy)
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

    return file_metadata['size'], file_metadata['content_type'], json.loads(file_metadata['storage_blocks']), file_metadata['strategy']
