from flask import Flask, request, make_response
import os
import sys

app = Flask(__name__)

cache = {}

@app.route("/file", methods=["POST"])
def add_file():
    payload = request.form
    files = request.files
    print(files)
    if not files or not files.get("file"):
        return make_response("File not found", 400)

    file = files.get("file")
    file_data = bytearray(file.read())

    try:
        with open(f"./files/{file.filename}.bin", "wb") as f:
            f.write(file_data)
    except EnvironmentError as e:
        print(f"Error writing file: {file.filename}")
        print(e)
        return make_response("Error saving file", 500)

    return "", 200


@app.route("/file/<filename>", methods=["GET"])
def get_file(filename):
    if filename in cache:
        print("hit cache")
        return cache[filename]

    try:
        with open(f"./files/{filename}.bin", "rb") as f:
            file = f.read()
    except FileNotFoundError:
        return make_response("File does not exist", 404)

    if filename not in cache:
        print("not in cache")
        cache[filename] = file

    return file


data_folder = sys.argv[1] if len(sys.argv) > 1 else "./files"

try:
    os.mkdir("./files")
except FileExistsError as _:
    # Folder exists
    pass

app.run(host="0.0.0.0", port=3000)
