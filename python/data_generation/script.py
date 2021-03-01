import numpy as np
import requests

FILE_SIZE = 10240
CHUNK_SIZE = 1024
BASE_SIZE = 992
ZEROS_SIZE = 960
ZEROS = bytearray(ZEROS_SIZE)


def generate_chunk():
    values = np.random.normal(128, 35, size=CHUNK_SIZE-ZEROS_SIZE)
    as_bytes = values.astype(np.uint8).tobytes()

    chunk = ZEROS + as_bytes

    return chunk

def generate_file(file_name):
    content = bytearray()

    for n in range(0, FILE_SIZE // CHUNK_SIZE):
        chunk = generate_chunk()
        content += chunk
    
    print(len(content))
    return content

    # with open(f"./{file_name}", "wb") as f:
    #     f.write(content)


for n in range(0,100):
    file_name = f"file_{n}"
    file_data = generate_file(file_name)
    requests.post(f"http://localhost:3000/file_data", files=dict(file=file_data), data=dict(file_name=file_name))



