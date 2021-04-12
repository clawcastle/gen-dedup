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

nodes = Nodes()
cache = Cache()

N_FRAGMENTS = 4
N_NEEDED_FRAGMENTS = 1

RS_CAUCHY_COEFFS = [
    bytearray([253, 126, 255, 127]),
    bytearray([126, 253, 127, 255]),
    bytearray([255, 127, 253, 126]),
    bytearray([127, 255, 126, 253]),
]

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
    # Make sure we can realize N_NEEDED_FRAGMENTS with 4 storage nodes
    assert(N_NEEDED_FRAGMENTS >= 0)
    assert(N_NEEDED_FRAGMENTS < N_FRAGMENTS)

    # How many coded fragments (=symbols) will be required to reconstruct the encoded data.
    symbols = N_FRAGMENTS - N_NEEDED_FRAGMENTS
    # The size of one coded fragment (total size/number of symbols, rounded up)
    symbol_size = math.ceil(len(file_data)/symbols)
    # Kodo RLNC encoder using 2^8 finite field
    encoder = kodo.RLNCEncoder(kodo.field.binary8, symbols, symbol_size)
    encoder.set_symbols_storage(file_data)

    encoded_fragments = []

    # Generate one coded fragment for each Storage Node
    for i in range(N_FRAGMENTS):
        # Select the next Reed Solomon coefficient vector
        coefficients = RS_CAUCHY_COEFFS[i]
        # Generate a coded fragment with these coefficients
        # (trim the coeffs to the actual length we need)
        symbol = encoder.produce_symbol(coefficients[:symbols])
        # Generate a random name for it and save
        name = random_string(8)
        #encoded_fragments.append(name)

        encoded_fragments.append({
            "name": name,
            "data": coefficients[:symbols] + bytearray(symbol)
        })

    return encoded_fragments

def save_file_data_and_metadata(file_data, file_name, file_length, content_type):
    encoded_fragments = encode_file(file_data)

    fragment_names = []
    metadata_dict = {}
    for fragment in encoded_fragments:
        fragment_names.append(fragment['name'])

        node_id = nodes.get_next_storage_node()

        requests.post(f"http://{node_id}/block", files=dict(block=fragment["data"]), data=dict(block_name=fragment["name"]))

        metadata_dict[fragment['name']] = node_id

    save_metadata(file_name, file_length, content_type, metadata_dict, "CODED")

def decode_file(symbols):
    """
    Decode a file using Reed Solomon decoder and the provided coded symbols.
    The number of symbols must be the same as N_FRAGMENTS - N_NEEDED_FRAGMENTS.

    :param symbols: coded symbols that contain both the coefficients and symbol data
    :return: the decoded file data
    """

    # Reconstruct the original data with a decoder
    symbols_num = len(symbols)
    symbol_size = len(symbols[0]['data']) - symbols_num #subtract the coefficients' size
    decoder = kodo.RLNCDecoder(kodo.field.binary8, symbols_num, symbol_size)
    data_out = bytearray(decoder.block_size())
    decoder.set_symbols_storage(data_out)

    for symbol in symbols:
        # Separate the coefficients from the symbol data
        coefficients = symbol['data'][:symbols_num]
        symbol_data = symbol['data'][symbols_num:]
        # Feed it to the decoder
        decoder.consume_symbol(symbol_data, coefficients)

    # Make sure the decoder successfully reconstructed the file
    assert(decoder.is_complete())

    return data_out

def get_file(filename, size, fragments):
    coded_fragments = [*fragments]
        
    # We need 4-N_NEEDED_FRAGMENTSfragments to reconstruct the file, select this many 
    # by randomly removing 'N_NEEDED_FRAGMENTS' elements from the given chunk names. 
    fragnames = copy.deepcopy(coded_fragments)

    for i in range(N_NEEDED_FRAGMENTS):
        fragnames.remove(random.choice(fragnames))
    
    symbols = []
    hits = 0
    # Request the coded fragments in parallel
    for name in fragnames:
        cache_val = cache.get_from_cache(name, filename)
        if cache_val is not None:
            hits += 1
            symbols.append({
                "chunkname": name, 
                "data": bytearray(cache_val)
            })
        else:
            req = requests.get(f"http://{fragments[name]}/block/{name}")
            req_val = req.content
            symbols.append({
                "chunkname": name, 
                "data": bytearray(req_val)
            })
            cache.add_to_cache(name, req_val)

    #Reconstruct the original file data
    file_data = decode_file(symbols)

    if measuring:
        with open(csvfile, "a") as f:
            writer = csv.DictWriter(f, fieldnames=labels)
            writer.writerow({"filename": filename, "n_blocks": len(fragnames), "cache_hits": hits})

    # file = b"".join(file_blocks)
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