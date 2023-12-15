# Enhanced version of hfsum (support Windows OS, Mac OS, Linux OS)
# todo: build using pyinstaller (support multi os platform), use try-except to sanitize input
import os
import datetime
import argparse
import hashlib
import ehfsum_exception as ehfsumerr
import stat
import itertools
from tabulate import tabulate

INVALID_PATH = "Invalid file path/name. Path %s does not exist."
SUPPORTED_ALGORITHMS = ["sha3_224", "sha3_256", "sha3_384", "sha3_512", "blake2b", "blake2s"]

def metadata(path):
    created_timestamp = os.path.getctime(path)
    created_datetime = datetime.datetime.fromtimestamp(created_timestamp)
    file_stat = os.stat(path)

    file_verbose = {
        "Absolute Path": os.path.abspath(path),
        "File Extension": os.path.splitext(path)[1],
        "File Created": created_datetime,
        "File Size": file_stat.st_size,
        "File Permissions": stat.filemode(file_stat.st_mode), 
    }

    tee_output = itertools.tee(file_verbose.items(), 2) 

    with open('metadata.txt', 'a') as meta:
        for key, value in tee_output[0]:
            print(f"{key}: {value}", file=meta)
    meta.close()

    print("\n")
    for key, value in tee_output[1]:
        print(f"{key}: {value}")

def save_hash(algorithm, digest, path):
    with open('hash.txt', 'a') as h:
        print(f"{algorithm}: {digest}", file=h)
    h.close()

def validate_path(path):
    if not valid_path(path):
        print("\n" + INVALID_PATH % (path))
        quit()

def validate_chunk_size(chunk_size):
    try:
        if chunk_size < 0:
            raise ehfsumerr.InvalidChunkSize(chunk_size)
        return chunk_size
    except ehfsumerr.InvalidChunkSize as e:
        print("Invalid chunk size! Please enter a non-negative integer:", e)
        quit()

def valid_path(path):
    return os.path.exists(path)

def hash(args):
    validate_path(args.hash[0])
    hash_table = []
    for algorithm in SUPPORTED_ALGORITHMS:
        hasher = hashlib.new(algorithm)

        with open(args.hash[0], 'rb') as file:
            while True:
                chunk = file.read(args.chunk)  # Read a chunk of n bytes
                if not chunk:
                    break
                hasher.update(chunk)
        ALGO = algorithm.upper()
        HEXDIGEST = hasher.hexdigest()
        hash_table.append([ALGO, HEXDIGEST])

        if args.save is not None:
            save_hash(ALGO, HEXDIGEST, args.hash[0])
    
    print(tabulate(hash_table, headers=["Algorithm", "Hash Value"], tablefmt="roundedgrid", stralign="grid"))

    if args.verbose_meta is not None:
        metadata(args.hash[0])

def main():
    parser = argparse.ArgumentParser(
        prog="ehfsum",
        description=("An Enhanced File Digest Generator."),
        epilog=("Hit Me Up @https://github.com/binaryassasins")
    )

    parser.add_argument("-hf", "--hash", 
                        type=str, 
                        nargs=1, 
                        metavar="path", 
                        default=None, 
                        help="get the hash value of specified path. (required)")
    # Custom chunk size
    parser.add_argument("-c", "--chunk", 
                        type=int,
                        nargs='?',  
                        metavar="chunk size", 
                        default=1024, 
                        help="explicit number of chunks to be processed. (optional)")
    # Save the hash
    parser.add_argument("-s", "--save", 
                        type=str, 
                        nargs='?', 
                        metavar="path", 
                        const="hash.txt",
                        default=None, 
                        help="save file hashes at the specified path. (optional)")
    # Save MetaData
    parser.add_argument("-vm", "--verbose_meta", 
                        type=str,
                        nargs='?',
                        metavar="path",
                        const="metadata.txt", 
                        default=None,  
                        help="save file metadata. (optional)")
    
    args = parser.parse_args()

    if args.hash is not None:
        if args.chunk is not None:
            args.chunk = validate_chunk_size(args.chunk)
        hash(args)
    else:
        print("Invalid! Please specify a file.")

if __name__ == "__main__":
    main()
