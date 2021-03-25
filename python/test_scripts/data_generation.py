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


# def create_block_hash_and_deviation(block):
#     base = block[:BASE_SIZE]
#     deviation = block[BASE_SIZE:]

#     md5_hash = hashlib.md5(base)
#     base_id = md5_hash.digest().hex()

#     return base_id, deviation

    # with open(f"./{file_name}", "wb") as f:
    #     f.write(content)

file_name_range = range(0,settings.N_FILES)

# data = {}

def generate_file(file_name):
    content = bytearray()

    for n in range(0, settings.FILE_SIZE // settings.CHUNK_SIZE):
        chunk = generate_chunk()
        # chunk_hash, deviation = create_block_hash_and_deviation(chunk)

        # if chunk_hash not in data:
        #     data[chunk_hash] = 1
        # else:
        #     data[chunk_hash] = data[chunk_hash] + 1

        content += chunk
    return content

for n in file_name_range:
    filename = f"file_{n}"
    file_data = generate_file(filename)

# plt.bar(data.keys(), data.values())

# plt.show()

print("Sending post requests")
for n in file_name_range:
    file_name = f"GEN_DEDUP_{n}"
    file_data = generate_file(file_name)
    requests.post(f"http://localhost:3000/file_data", files=dict(file=file_data), data=dict(file_name=file_name))
print("Completed post requests")

# request_file_ids = list(map(lambda x: math.floor(x), truncnorm.rvs((0-MEAN)/SIGMA,(N_FILES-1-MEAN)/SIGMA,loc=MEAN,scale=SIGMA,size=N_REQUESTS)))

# print("Starting get requests")
# timings = []
# labels = ["request_id", "file_id", "elapsed_time"]
# for i, id in enumerate(request_file_ids):
#     file_name = f"file_{id}"
#     start = time()
#     response = requests.get(f"http://localhost:3000/file/{file_name}")
#     elapsed = time() - start
#     timings.append({
#         "request_id": i,
#         "file_id": id,
#         "elapsed_time": elapsed
#     })

# filename = f"./timings_{MEAN}_{SIGMA}_{N_REQUESTS}_{N_FILES}.csv"

# with open(filename, "a", newline='') as f:
#     writer = csv.DictWriter(f, fieldnames=labels)
#     writer.writeheader()
#     for elem in timings:
#         writer.writerow(elem)


