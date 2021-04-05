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

def generate_chunk():
    values = np.random.normal(128, settings.SD_BYTES, size=settings.CHUNK_SIZE-settings.ZEROS_SIZE)
    as_bytes = values.astype(np.uint8).tobytes()

    chunk = ZEROS + as_bytes

    return chunk

file_name_range = range(0,settings.N_FILES)

def generate_file(file_name):
    content = bytearray()

    for n in range(0, settings.FILE_SIZE // settings.CHUNK_SIZE):
        chunk = generate_chunk()

        content += chunk
    return content

print("Sending post requests")

sd_bytes = [5, 10, 20, 40, 60, 80, 120]

for sd in sd_bytes:
    settings.SD_BYTES = sd
    for n in file_name_range:
        file_name = f"GEN_DEDUP_SD{sd}_{n}"
        file_data = generate_file(file_name)
        requests.post(f"http://localhost:3000/file_data", files=dict(file=file_data), data=dict(file_name=file_name))

print("Completed post requests")


