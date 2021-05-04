from flask import Flask, request, make_response, jsonify
import os
from random import randint
import base64
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

node_id = os.environ.get("NODE_ID") if os.environ.get("NODE_ID") is not None else str(randint(0, 1000))
port = int(os.environ.get("PORT_NO")) if os.environ.get("PORT_NO") is not None else randint(3001, 10000)


@app.route("/block", methods=["POST"])
def add_block():
    files = request.files
    block = files.get("block")
    block_data = bytearray(block.read())
    block_name = request.form.get("block_name")

    if not files or not files.get("block"):
        return make_response("File not found", 400)

    block = files.get("block")

    try:
        with open(f"./data/{block_name}.bin", "wb") as f:
            f.write(block_data)
    except EnvironmentError as e:
        print(f"Error writing file: {block_name}", flush=True)
        print(e)
        return make_response("Error saving file", 500)

    return "", 200

@app.route("/fragments", methods=["POST"])
def add_fragments():
    if not request.files:
        return make_response("No data", 400)

    for key, sub_frag in request.files.items():
        data = bytearray(sub_frag.read())
        try:
            with open(f"./data/{key}.bin", "wb") as f:
                f.write(data)
        except EnvironmentError as e:
            print(f"Error writing fragment: {key}", flush=True)
            print(e)
            return make_response("Error saving fragment", 500)
    
    return "", 200

@app.route("/fragments/<fragment_name>/<n_sub_fragments>", methods=["GET"])
def get_sub_fragments(fragment_name, n_sub_fragments):
    sub_frag_dict = {}
    for i in range(int(n_sub_fragments)):
        try:
            with open(f"./data/{fragment_name}.{i}.bin", "rb") as f:
                subfrag = f.read()
                subfrag_b64 = base64.b64encode(subfrag).decode("utf-8")
                sub_frag_dict[f"{fragment_name}.{i}"] = subfrag_b64
        except FileNotFoundError:
            return make_response("File does not exist", 404)
    
    return jsonify(sub_frag_dict)

@app.route("/block/<blockname>", methods=["GET"])
def get_block(blockname):
    try:
        with open(f"./data/{blockname}.bin", "rb") as f:
            block = f.read()
    except FileNotFoundError:
        return make_response("File does not exist", 404)

    return block

app.run(host="0.0.0.0", port=port)