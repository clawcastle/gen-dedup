from flask import Flask, request, make_response, send_file
import os
import sys
import io
from random import randint
import hashlib
from namenode import *
import requests
from database import Database
from nodes import Nodes
from measurement_session import get_settings, put_setting, clear_session
put_setting("cache_size", int(os.environ.get("CACHE_SIZE")))

import dedup as dedup
import gen_dedup as gen_dedup
import full_file as full_file
import coded as coded

BLOCK_SIZE = 1024

app = Flask(__name__)
nodes = Nodes()

node_id = os.environ.get("NODE_ID") if os.environ.get("NODE_ID") is not None else str(randint(0, 1000))
port = int(os.environ.get("PORT_NO")) if os.environ.get("PORT_NO") is not None else 3000
strategy = os.environ.get("STRATEGY") if os.environ.get("STRATEGY") is not None else "FULL_FILE"

print(f"Strategy: {strategy}.")


@app.route("/file", methods=["POST"])
def add_file():
    files = request.files
    if not files or not files.get("file"):
        return make_response("File not found", 400)

    file = files.get("file")
    file_data = bytearray(file.read())
    file_length = len(file_data)
    content_type = file.mimetype
    save_file_data_and_metadata(file_data, file.filename, file_length, content_type)
    return "", 200

@app.route("/file_data", methods=["POST"])
def add_file_data():
    files = request.files
    file = files.get("file")
    file_data = bytearray(file.read())
    file_length = len(file_data)
    file_name = request.form.get("file_name")
    content_type = ".bin"

    save_file_data_and_metadata(file_data, file_name, file_length, content_type)
    return "", 200

def save_file_data_and_metadata(file_data, file_name, file_length, content_type):
    if strategy == "FULL_FILE":
        full_file.save_file_data_and_metadata(file_data, file_name, file_length, content_type)
    elif strategy == "CODED":
        coded.save_file_data_and_metadata(file_data, file_name, file_length, content_type)
    elif strategy == "DEDUP":
        dedup.save_file_data_and_metadata(file_data, file_name, file_length, content_type)
    elif strategy == "GEN_DEDUP":
        gen_dedup.save_file_data_and_metadata(file_data, file_name, file_length, content_type)
    elif strategy == "CODED":
        coded.save_file_data_and_metadata(file_data, file_name, file_length, content_type)

@app.route("/file/<filename>", methods=["GET"])
def get_file(filename):
    try:
        size, content_type, blocks, strategy = get_metadata(filename)
    except:
        return make_response("File does not exist", 404)

    if strategy == "FULL_FILE":
        file_data = full_file.get_file(filename, size, blocks)
    elif strategy == "CODED":
        file_data = coded.get_file(filename, size, blocks)
    elif strategy == "DEDUP":
        file_data = dedup.get_file(filename, size, blocks)
    elif strategy == "GEN_DEDUP":
        file_data = gen_dedup.get_file(filename, size, blocks)
    elif strategy == "CODED":
        file_data = coded.get_file(filename, size, blocks)

    return send_file(file_data, mimetype=content_type, as_attachment=True, attachment_filename=filename)


@app.route("/measurements/session/start", methods=["POST"])
def start_measurement_session():
    put_setting("sd_files", request.form["sd_files"])
    put_setting("sd_bytes", request.form["sd_bytes"])
    put_setting("mean_files", request.form["mean_files"])
    put_setting("mean_bytes", request.form["mean_bytes"])
    put_setting("scenario", request.form["scenario"])
    put_setting("n_files", request.form["n_files"])
    put_setting("n_requests", request.form["n_requests"])
    put_setting("cache_size", int(request.form["cache_size"]))

    if strategy == "FULL_FILE":
        full_file.new_measurement_session()
    elif strategy == "CODED":
        print("coded", flush=True)
        coded.new_measurement_session()
    elif strategy == "DEDUP":
        dedup.new_measurement_session()
    elif strategy == "GEN_DEDUP":
        gen_dedup.new_measurement_session()

    return "", 200


data_folder = sys.argv[1] if len(sys.argv) > 1 else "./files"

try:
    os.mkdir("./files")
except FileExistsError as _:
    # Folder exists
    pass

app.run(host="0.0.0.0", port=port)
