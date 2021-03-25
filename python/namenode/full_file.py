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
measuring = bool(os.environ.get("MEASUREMENT_MODE"))
CACHE_STRATEGY = os.environ.get("CACHE_STRATEGY")
labels = ["filename", "n_blocks", "cache_hits"]

def save_file_data_and_metadata(file_data, file_name, file_length, content_type):
    node_id = get_block_storage_node(file_name)
    if not node_id:
        new_node_id = nodes.get_next_storage_node()
        save_block_node_association(file_name, new_node_id)
        requests.post(f"http://{new_node_id}/block", files=dict(block=file_data), data=dict(block_name=file_name))
        save_metadata(file_name, file_length, content_type, {}, "FULL_FILE")

def get_file(file_name, size, blocks):
    node_id = get_block_storage_node(file_name)
    hits = 0
    file_data = cache.get_from_cache(file_name, file_name)

    if file_data is not None:
        hits = 1
    else:
        req = requests.get(f"http://{node_id}/block/{file_name}")
        file_data = req.content
        cache.add_to_cache(file_name, file_data)

    if measuring:
        with open(csvfile, "a") as f:
                writer = csv.DictWriter(f, fieldnames=labels)
                writer.writerow({"filename": file_name, "n_blocks": "", "cache_hits": hits})

    return io.BytesIO(file_data)


def new_measurement_session():
    if measuring:
        settings = get_settings()
        cache_size = settings["cache_size"]
        folder_path = f'./measurements/Scenario{settings["scenario"]}/CACHE_SIZE={cache_size}_NFILES={settings["n_files"]}/{CACHE_STRATEGY}_SDF={settings["sd_files"]}_SDB={settings["sd_bytes"]}'
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        global csvfile
        csvfile = folder_path + f"/get_file_request.csv"
        with open(csvfile, "w") as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writeheader()

        cache.new_measurement_session()


