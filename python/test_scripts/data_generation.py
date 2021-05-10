import numpy as np
import requests
from scipy.stats import truncnorm
import math
from time import time
import csv
import hashlib
import matplotlib.pyplot as plt
import settings

ZEROS = bytearray(settings.ZEROS_SIZE)

max16 = math.pow(2, 16)
max8 = math.pow(2, 8)

def generate_chunk():
    base = np.random.normal(max16 // 2, settings.SD_BYTES, size=1).astype(np.uint16).tobytes()
    deviation = np.random.normal(max8 // 2, 30, size=1).astype(np.uint8).tobytes()

    chunk = ZEROS + base + deviation

    return chunk

file_name_range = range(0,settings.N_FILES)

def generate_file(file_name):
    content = bytearray()

    for n in range(0, settings.FILE_SIZE // settings.CHUNK_SIZE):
        chunk = generate_chunk()

        content += chunk
    return content

print("Sending post requests")
for n in file_name_range:
    file_name = f"{settings.SCENARIO}_{n}"
    file_data = generate_file(file_name)
    requests.post(f"http://localhost:3000/file_data", files=dict(file=file_data), data=dict(file_name=file_name))
print("Completed post requests")


