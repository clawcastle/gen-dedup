import requests
import hashlib
from nodes import Nodes
from namenode import *
import io
from cache import Cache

nodes = Nodes()
cache = Cache()

BLOCK_SIZE = 1024

def save_file_data_and_metadata(file_data, file_name, file_length, content_type):
    existing, missing = create_blocks_and_hashes(file_data)
    print(len(existing))
    
    block_node_assocations = {}

    for _, block_meta in missing.items():
        block_id = block_meta["block_id"]
        node_id = nodes.get_next_storage_node()
        requests.post(f"http://{node_id}/block", files=dict(block=file_data), data=dict(block_name=block_id))

        if not block_id in block_node_assocations:
            block_node_assocations[block_id] = node_id
            save_block_node_association(block_id, node_id)


        block_meta["node_id"] = block_node_assocations[block_id]

    block_dic = existing | missing

    save_metadata(file_name, file_length, content_type, block_dic, "DEDUP")

def create_blocks_and_hashes(file_data):
    existing, missing = {}, {}

    chunks = [file_data[i:i+BLOCK_SIZE] for i in range(0, len(file_data), BLOCK_SIZE)]

    for count, chunk in enumerate(chunks):
        md5_hash = hashlib.md5(chunk)
        block_id = md5_hash.digest().hex()

        node_id = get_block_storage_node(block_id)

        if not node_id:
            missing[count] = {'block_id': block_id, 'node_id': node_id}
        else:
            existing[count] = {'block_id': block_id, 'node_id': node_id}

    return existing, missing


def get_file(filename, size, blocks):
    file_blocks = [None] * len(blocks.keys())

    for order, block_meta in blocks.items():
        block_id = block_meta["block_id"]
        node_id = block_meta["node_id"]

        cache_val = cache.get_from_cache(block_id)
        if cache_val is not None:
            print("hit cache", flush=True)
            file_blocks[int(order)] = cache_val
        else:
            print("not in cache", flush=True)
            req = requests.get(f"http://{node_id}/block/{block_id}")
            block_val = req.content
            cache.add_to_cache(block_id, block_val)

            file_blocks[int(order)] = block_val

    file = b"".join(file_blocks)
    return io.BytesIO(file)

    # return send_file(io.BytesIO(file), mimetype=content_type, as_attachment=True, attachment_filename=filename)