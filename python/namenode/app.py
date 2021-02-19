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
from nodes import Nodes

BLOCK_SIZE = 10000

app = Flask(__name__)
nodes = Nodes()
cache = Cache()

node_id = os.environ.get("NODE_ID") if os.environ.get("NODE_ID") is not None else str(randint(0, 1000))
port = int(os.environ.get("PORT_NO")) if os.environ.get("PORT_NO") is not None else 3000


@app.route("/file", methods=["POST"])
def add_file():
    files = request.files
    if not files or not files.get("file"):
        return make_response("File not found", 400)

    file = files.get("file")
    file_data = bytearray(file.read())
    file_length = len(file_data)
    content_type = file.mimetype
    existing, missing = create_blocks_and_hashes(file_data)

    block_node_assocations = {}

    for _, block_meta in missing.items():
        block_id = block_meta["block_id"]
        node_id = nodes.get_next_storage_node()
        requests.post(f"http://{node_id}/block", files=dict(block=file_data), data=dict(block_name=block_id))

        if not block_id in block_node_assocations:
            block_node_assocations[block_id] = node_id
            save_block_node_association(block_id, node_id)


        block_meta["node_id"] = block_node_assocations[block_id]

    block_dic = existing | missing

    save_metadata(file.filename, file_length, content_type, block_dic)
    return "", 200


def create_blocks_and_hashes(file_data):
    existing, missing = {}, {}

    chunks = [file_data[i:i+BLOCK_SIZE] for i in range(0, len(file_data), BLOCK_SIZE)]

    for count, chunk in enumerate(chunks):
        md5_hash = hashlib.md5(chunk)
        block_id = md5_hash.digest().hex()

        node_id = get_block_storage_node(block_id)

        if not node_id:
            missing[count] = {'block_id': block_id, 'node_id': node_id}
        else:
            existing[count] = {'block_id': block_id, 'node_id': node_id}

    return existing, missing


@app.route("/file/<filename>", methods=["GET"])
def get_file(filename):
    try:
        size, content_type, blocks = get_metadata(filename)
    except:
        return make_response("File does not exist", 404)

    file_blocks = [None] * len(blocks.keys())

    for order, block_meta in blocks.items():
        block_id = block_meta["block_id"]
        node_id = block_meta["node_id"]

        cache_val = cache.get_from_cache(block_id)
        if cache_val is not None:
            print("hit cache", flush=True)
            file_blocks[int(order)] = cache_val
        else:
            print("not in cache", flush=True)
            req = requests.get(f"http://{node_id}/block/{block_id}")
            block_val = req.content
            cache.add_to_cache(block_id, block_val)

            file_blocks[int(order)] = block_val

    file = b"".join(file_blocks)

    return send_file(io.BytesIO(file), mimetype=content_type, as_attachment=True, attachment_filename=filename)


data_folder = sys.argv[1] if len(sys.argv) > 1 else "./files"

try:
    os.mkdir("./files")
except FileExistsError as _:
    # Folder exists
    pass

app.run(host="0.0.0.0", port=port)
