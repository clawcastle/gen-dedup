import requests
import hashlib
from nodes import Nodes
from namenode import *
import io
from cache import Cache
import os
from measurement_session import get_settings
from pathlib import Path
import csv

nodes = Nodes()
cache = Cache()

BLOCK_SIZE = int(os.environ.get("BLOCK_SIZE"))
BASE_SIZE = int(os.environ.get("BASE_SIZE"))
measuring = bool(os.environ.get("MEASUREMENT_MODE"))
CACHE_STRATEGY = os.environ.get("CACHE_STRATEGY")
labels = ["filename", "n_blocks", "cache_hits"]

def save_file_data_and_metadata(file_data, file_name, file_length, content_type):
    existing, missing, new_blocks = create_blocks_and_hashes(file_data)
    
    block_node_assocations = {}

    for _, block_meta in missing.items():
        base_id = block_meta["base_id"]
        chunk = new_blocks[base_id]

        node_id = nodes.get_next_storage_node()
        requests.post(f"http://{node_id}/block", files=dict(block=chunk[:BASE_SIZE]), data=dict(block_name=base_id))

        if not base_id in block_node_assocations:
            block_node_assocations[base_id] = node_id
            save_block_node_association(base_id, node_id)


        block_meta["node_id"] = block_node_assocations[base_id]

    block_dic = existing | missing

    save_metadata(file_name, file_length, content_type, block_dic, "GEN_DEDUP")

def create_block_hash_and_deviation(block):
    base = block[:BASE_SIZE]
    deviation = block[BASE_SIZE:]

    md5_hash = hashlib.md5(base)
    base_id = md5_hash.digest().hex()

    return base_id, deviation


def create_blocks_and_hashes(file_data):
    existing, missing, new_blocks = {}, {}, {}

    chunks = [file_data[i:i+BLOCK_SIZE] for i in range(0, len(file_data), BLOCK_SIZE)]

    for count, chunk in enumerate(chunks):
        base_id, deviation = create_block_hash_and_deviation(chunk)

        node_id = get_block_storage_node(base_id)

        if not node_id:
            missing[count] = {'base_id': base_id, 'node_id': node_id, 'deviation': bytes(deviation).hex()}
            new_blocks[base_id] = chunk
        else:
            print(f"block with id: {base_id} exists already.")
            existing[count] = {'base_id': base_id, 'node_id': node_id, 'deviation': bytes(deviation).hex()}

    return existing, missing, new_blocks


def get_file(filename, size, blocks):
    file_blocks = [None] * len(blocks.keys())
    hits = 0
    for order, block_meta in blocks.items():
        base_id = block_meta["base_id"]
        node_id = block_meta["node_id"]
        deviation_hex = block_meta["deviation"]
        deviation = bytearray.fromhex(deviation_hex)

        cache_val = cache.get_from_cache(base_id, filename)
        if cache_val is not None:
            file_blocks[int(order)] = cache_val + deviation
            hits += 1
        else:
            req = requests.get(f"http://{node_id}/block/{base_id}")
            block_val = req.content
            cache.add_to_cache(base_id, block_val)

            file_blocks[int(order)] = block_val + deviation

    if measuring:
        with open(csvfile, "a") as f:
                writer = csv.DictWriter(f, fieldnames=labels)
                writer.writerow({"filename": filename, "n_blocks": len(file_blocks), "cache_hits": hits})
        
    file = b"".join(file_blocks)
    return io.BytesIO(file)


def new_measurement_session():
    if measuring:
        cache_size = int(os.environ.get("CACHE_SIZE"))
        settings = get_settings()
        folder_path = f'./measurements/Scenario{settings["scenario"]}/CACHE_SIZE={cache_size}_NFILES={settings["n_files"]}/{CACHE_STRATEGY}_SDF={settings["sd_files"]}_SDB={settings["sd_bytes"]}'
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        global csvfile
        csvfile = folder_path + f"/get_file_request.csv"
        with open(csvfile, "w") as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writeheader()

        cache.new_measurement_session()