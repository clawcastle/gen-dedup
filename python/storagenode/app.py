from flask import Flask, request, make_response

app = Flask(__name__)

@app.route("/block", methods=["POST"])
def add_block():
    files = request.files
    block = files.get("block")
    block_data = bytearray(block.read())
    block_name = request.form.get("block_name")
    print(f"block: {block_name}, {request.form}")

    if not files or not files.get("block"):
        return make_response("File not found", 400)

    block = files.get("block")

    try:
        with open(f"./files/{block_name}.bin", "wb") as f:
            f.write(block_data)
    except EnvironmentError as e:
        print(f"Error writing file: {block_name}")
        print(e)
        return make_response("Error saving file", 500)

    return "", 200

@app.route("/file/<blockname>", methods=["GET"])
def get_block(blockname):
    try:
        with open(f"./files/{blockname}.bin", "rb") as f:
            block = f.read()
    except FileNotFoundError:
        return make_response("File does not exist", 404)

    return block

app.run(host="0.0.0.0", port=3001)