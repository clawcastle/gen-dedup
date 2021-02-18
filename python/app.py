from flask import Flask, request, make_response
import os
import sys
import hashlib
from cache import Cache
from namenode.namenode import *

app = Flask(__name__)
cache = Cache()


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
    block_dic = create_blocks_and_hashes(file_data)

    save_metadata(file.filename, file_length, content_type, block_dic)

    try:
        with open(f"./files/{file.filename}.bin", "wb") as f:
            f.write(file_data)
    except EnvironmentError as e:
        print(f"Error writing file: {file.filename}")
        print(e)
        return make_response("Error saving file", 500)

    return "", 200


def create_blocks_and_hashes(file_data):
    md5_hash = hashlib.md5(file_data)
    block_id = str(md5_hash.digest())

    return {block_id: {'order': 0, 'node_id': 'xxx'}}


@app.route("/file/<filename>", methods=["GET"])
def get_file(filename):
    content = cache.get_from_cache(filename)
    if content is not None:
        print("hit cache")
        return content

    try:
        with open(f"./files/{filename}.bin", "rb") as f:
            file = f.read()
    except FileNotFoundError:
        return make_response("File does not exist", 404)

    if not cache.is_in_cache(filename):
        print("not in cache")
        cache.add_to_cache(filename, file)

    return file


data_folder = sys.argv[1] if len(sys.argv) > 1 else "./files"

try:
    os.mkdir("./files")
except FileExistsError as _:
    # Folder exists
    pass

app.run(host="0.0.0.0", port=3000)
