import kodo
import math
import random
import copy # for deepcopy
import json

N_FRAGMENTS = 12
N_NEEDED_FRAGMENTS = 10

RS_CAUCHY_COEFFS = [
    bytearray([253, 126, 255, 127]),
    bytearray([126, 253, 127, 255]),
    bytearray([255, 127, 253, 126]),
    bytearray([127, 255, 126, 253])
]

def random_string(length=8):
    """
    Returns a random alphanumeric string of the given length. 
    Only lowercase ascii letters and numbers are used.
    :param length: Length of the requested random string 
    :return: The random generated string
    """
    return ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(length)])

def encode_file(file_data, N_NEEDED_FRAGMENTS):
    # Make sure we can realize N_NEEDED_FRAGMENTSwith 4 storage nodes
    assert(N_NEEDED_FRAGMENTS>= 0)
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


def store_file(file_data, N_NEEDED_FRAGMENTS, send_task_socket, response_socket):
    """
    Store a file using Reed Solomon erasure coding, protecting it against 'N_NEEDED_FRAGMENTS'
    unavailable storage nodes.
    The erasure coding part codes are the customized version of the 'encode_decode_using_coefficients'
    example of kodo-python, where you can find a detailed description of each step.

    :param file_data: The file contents to be stored as a Python bytearray
    :param N_NEEDED_FRAGMENTS: How many storage node failures should the data survive
    :param send_task_socket: A ZMQ PUSH socket to the storage nodes
    :param response_socket: A ZMQ PULL socket where the storage nodes respond
    :return: A list of the coded fragment names, e.g. (c1,c2,c3,c4)
    """

    fragment_names = []
    encoded_fragments = encode_file(file_data,N_NEEDED_FRAGMENTS)

    for i in range(len(encoded_fragments)):
        fragment = encoded_fragments[i]
        fragment_names.append(fragment['name'])
        task.filename = fragment['name']

        send_task_socket.send_multipart([
            task.SerializeToString(),
            fragment['data']
        ])

    for task_nbr in encoded_fragments:
        resp = response_socket.recv_pyobj()

    return fragment_names




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

    print(f"syms: {symbols}")
    for symbol in symbols:
        # Separate the coefficients from the symbol data
        coefficients = symbol['data'][:symbols_num]
        symbol_data = symbol['data'][symbols_num:]
        # Feed it to the decoder
        decoder.consume_symbol(symbol_data, coefficients)

    # Make sure the decoder successfully reconstructed the file
    assert(decoder.is_complete())
    print("File decoded successfully")

    return data_out
#


def get_file(coded_fragments, N_NEEDED_FRAGMENTS, file_size,
             data_req_socket, response_socket):
    """
    Implements retrieving a file that is stored with Reed Solomon erasure coding

    :param coded_fragments: Names of the coded fragments
    :param N_NEEDED_FRAGMENTS: Max erasures setting that was used when storing the file
    :param file_size: The original data size. 
    :param data_req_socket: A ZMQ SUB socket to request chunks from the storage nodes
    :param response_socket: A ZMQ PULL socket where the storage nodes respond.
    :return: A list of the random generated chunk names, e.g. (c1,c2), (c3,c4)
    """
    
    # We need 4-N_NEEDED_FRAGMENTSfragments to reconstruct the file, select this many 
    # by randomly removing 'N_NEEDED_FRAGMENTS' elements from the given chunk names. 
    fragnames = copy.deepcopy(coded_fragments)

    print(f"frags: {fragnames}")
    for i in range(N_NEEDED_FRAGMENTS):
        fragnames.remove(random.choice(fragnames))
    
    # Request the coded fragments in parallel
    for name in fragnames:
        task = None
        task.filename = name
        data_req_socket.send(
            task.SerializeToString()
            )

    # Receive all chunks and insert them into the symbols array
    symbols = []
    for _ in range(len(fragnames)):
        result = response_socket.recv_multipart()
        # In this case we don't care about the received name, just use the 
        # data from the second frame
        symbols.append({
            "chunkname": result[0].decode('utf-8'), 
            "data": bytearray(result[1])
        })
    print("All coded fragments received successfully")

    #Reconstruct the original file data
    file_data = decode_file(symbols)

    return file_data[:file_size]
#
