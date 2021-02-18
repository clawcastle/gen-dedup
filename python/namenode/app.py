from flask import Flask, request, make_response, send_file
import os
import sys
import io
from random import randint
import hashlib
from cache import Cache
from namenode import *
import requests
from database import Database

app = Flask(__name__)
cache = Cache()

node_id = os.environ.get("NODE_ID") if os.environ.get("NODE_ID") is not None else str(randint(0, 1000))
port = int(os.environ.get("PORT_NO")) if os.environ.get("PORT_NO") is not None else 3000


@app.route("/file", methods=["POST"])
def add_file():
    files = request.files
    print(files)
    if not files or not files.get("file"):
        return make_response("File not found", 400)

    file = files.get("file")
    file_data = bytearray(file.read())
    file_length = len(file_data)
    content_type = file.mimetype
    existing, missing = create_blocks_and_hashes(file_data)

    for block_id, block_meta in missing.items():
        requests.post("http://storagenode_1:3001/block", files=dict(block=file_data), data=dict(block_name=block_id))
        block_meta["node_id"] = "storagenode_1"
        save_block_node_association(block_id, "storagenode_1")

    block_dic = existing | missing

    save_metadata(file.filename, file_length, content_type, block_dic)
    return "", 200


def create_blocks_and_hashes(file_data):
    existing, missing = {}, {}

    md5_hash = hashlib.md5(file_data)
    block_id = md5_hash.digest().hex()

    node_id = get_block_storage_node(block_id)

    if not node_id:
        missing[block_id] = {'order': 0, 'node_id': node_id}
    else:
        existing[block_id] = {'order': 0, 'node_id': node_id}


    return existing, missing


@app.route("/file/<filename>", methods=["GET"])
def get_file(filename):
    print("halloooo")

    try:
        size, content_type, blocks = get_metadata(filename)
    except:
        return make_response("File does not exist", 404)

    print(f"blocks: {blocks}")
    k = list(blocks.keys())[0]
    print(f"k: {k}")


    content = cache.get_from_cache(k)
    if content is not None:
        print("hit cache")
        return content

    file_blocks = [None] * len(blocks.keys())

    for key, val in blocks.items():
        req = requests.get(f"http://storagenode_1:3001/block/{key}")
        block_val = req.content
        file_blocks[int(val["order"])] = block_val

    file = b"".join(file_blocks)

    if not cache.is_in_cache(k):
        print("not in cache")
        print(f"k: {k}")
        cache.add_to_cache(k, file)

    return send_file(io.BytesIO(file), mimetype=content_type, as_attachment=True, attachment_filename=filename)


data_folder = sys.argv[1] if len(sys.argv) > 1 else "./files"

try:
    os.mkdir("./files")
except FileExistsError as _:
    # Folder exists
    pass

app.run(host="0.0.0.0", port=port)
