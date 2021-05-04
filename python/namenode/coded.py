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
import kodo
import math
import random
import copy # for deepcopy
import json
import string
import requests
import base64

nodes = Nodes()
cache = Cache()

N_FRAGMENTS = 10
N_SUBFRAGMENTS = 2

measuring = bool(os.environ.get("MEASUREMENT_MODE"))
CACHE_STRATEGY = os.environ.get("CACHE_STRATEGY")
labels = ["filename", "n_blocks", "cache_hits"]

def random_string(length=8):
    """
    Returns a random alphanumeric string of the given length. 
    Only lowercase ascii letters and numbers are used.
    :param length: Length of the requested random string 
    :return: The random generated string
    """
    return ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(length)])

def encode_file(file_data):
    # How many coded subfragments (=symbols) will be required to reconstruct the encoded data.
    symbols = N_FRAGMENTS * N_SUBFRAGMENTS

    # The size of one coded subfragment (total size/number of symbols, rounded up)
    symbol_size = math.ceil(len(file_data)/symbols)

    # Kodo RLNC encoder using 2^8 finite field
    encoder = kodo.RLNCEncoder(kodo.field.binary8, symbols, symbol_size)
    encoder.set_symbols_storage(file_data)

    fragment_names = []

    fragment_dict = {}

    for i in range(N_FRAGMENTS):
        # Generate a random name for them and save
        name = random_string(8)
        fragment_names.append(name)

        subfragments = []

        for j in range(N_SUBFRAGMENTS):
            # Create a random coefficient vector
            coefficients = encoder.generate()
            # Generate a coded fragment with these coefficients
            symbol = encoder.produce_symbol(coefficients)
            subfragments.append(coefficients + bytearray(symbol))
        
        subfrag_dict = {}
        for i, subfrag in enumerate(subfragments):
            subfrag_dict[f"{name}.{i}"] = subfrag


        fragment_dict[name] = subfrag_dict
    
    return fragment_dict

def save_file_data_and_metadata(file_data, file_name, file_length, content_type):
    encoded_fragments = encode_file(file_data)
    metadata_dict = {}

    for fragment_name, subfrag_dict in encoded_fragments.items():
        node_id = nodes.get_next_storage_node()
        requests.post(f"http://{node_id}/fragments", files=subfrag_dict)
        metadata_dict[fragment_name] = node_id

    save_metadata(file_name, file_length, content_type, metadata_dict, "CODED")

def decode_file(symbols):
    # Reconstruct the original data with a decoder
    symbols_num = len(symbols)
    symbol_size = len(symbols[0]) - symbols_num #subtract the coefficients' size
    decoder = kodo.RLNCDecoder(kodo.field.binary8, symbols_num, symbol_size)
    data_out = bytearray(decoder.block_size())
    decoder.set_symbols_storage(data_out)

    for symbol in symbols:
        # Separate the coefficients from the symbol data
        coefficients = symbol[:symbols_num]
        symbol_data = symbol[symbols_num:]
        # Feed it to the decoder
        decoder.consume_symbol(symbol_data, coefficients)

    # Make sure the decoder successfully reconstructed the file
    assert(decoder.is_complete())

    return data_out

def get_file(filename, size, metadata_dict):
    cache_val = cache.get_from_cache(filename, filename)
    symbols = []
    counter = 0
    
    all_values = copy.deepcopy(cache_val)
    
    for fragment in cache_val:
        for _, subfragvals in fragment.items():
            symbols.extend(subfragvals)
    
    missing = [*metadata_dict]

    for fragment in cache_val:
        for fragname in [*fragment]:
            counter += 1
            if fragname not in missing:
                print(f"missing: {missing}, fragname: {fragname}", flush=True)
            missing.remove(fragname)
    
    for fragment_name in missing:
        subfrags = []
        node_id = metadata_dict[fragment_name]
        frag_response = requests.get(f"http://{node_id}/fragments/{fragment_name}/{N_SUBFRAGMENTS}")
        fragment_data = frag_response.json()
        for _, sub_frag_b64 in fragment_data.items():
            sub_frag_val = bytearray(base64.b64decode(sub_frag_b64))
            symbols.append(sub_frag_val)
            subfrags.append(sub_frag_val)
        all_values.append({fragment_name: subfrags})

    
    data = decode_file(symbols)

    cache.add_to_cache(filename, all_values)

    if measuring:
        with open(csvfile, "a") as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writerow({"filename": filename, "n_blocks": N_FRAGMENTS, "cache_hits": len(cache_val)})

    # file = b"".join(file_blocks)
    return io.BytesIO(data)

def new_measurement_session():
    if measuring:
        settings = get_settings()
        cache_size = settings["cache_size"]
        print(f"CACHE_SIZE: {cache_size}", flush=True)
        folder_path = f'./measurements/Scenario{settings["scenario"]}/CACHE_SIZE={cache_size}_NFILES={settings["n_files"]}/{CACHE_STRATEGY}_SDF={settings["sd_files"]}_SDB={settings["sd_bytes"]}'
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        global csvfile
        csvfile = folder_path + f"/get_file_request.csv"
        with open(csvfile, "w") as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writeheader()

        cache.new_measurement_session()