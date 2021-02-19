from flask import Flask, request, make_response
import os
from random import randint

app = Flask(__name__)

node_id = os.environ.get("NODE_ID") if os.environ.get("NODE_ID") is not None else str(randint(0, 1000))
port = int(os.environ.get("PORT_NO")) if os.environ.get("PORT_NO") is not None else randint(3001, 10000)


@app.route("/block", methods=["POST"])
def add_block():
    files = request.files
    block = files.get("block")
    block_data = bytearray(block.read())
    block_name = request.form.get("block_name")
    print(f"block: {block_name}, {request.form}", flush=True)

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

@app.route("/block/<blockname>", methods=["GET"])
def get_block(blockname):
    try:
        with open(f"./data/{blockname}.bin", "rb") as f:
            block = f.read()
    except FileNotFoundError:
        return make_response("File does not exist", 404)

    return block

print(f"port {port}")
app.run(host="0.0.0.0", port=port)