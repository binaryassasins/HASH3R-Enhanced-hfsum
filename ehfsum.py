# Enhanced version of hfsum (support Windows OS, Mac OS, Linux OS)
# todo: create customizable chunk size (default: 1024), create report generation (digest, file type, product version, product name, copyright, file location, file permissions, date and time the file was downloaded), build using pyinstaller (support multi os platform), use try-except to sanitize input
import os
import datetime
import argparse
import hashlib
import ehfsum_exception as ehfsumerr

INVALID_PATH = "Invalid file path/name. Path %s does not exist."
SUPPORTED_ALGORITHMS = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]  # Add more algorithms here

def metadata(path):
    created_timestamp = os.path.getctime(path)
    created_datetime = datetime.datetime.fromtimestamp(created_timestamp)
    with open('metadata.txt', 'a') as meta:
        print(f"Absolute File Path: {os.path.abspath(path)}", file=meta)
        print(f"File Type: {os.path.splitext(path)[1]}", file=meta)
        print(f"File Created: {created_datetime}\n", file=meta)
    meta.close()

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
        print(f"\n{ALGO}: {HEXDIGEST}", end='')

        if args.save is not None:
            save_hash(ALGO, HEXDIGEST, args.hash[0])
    
    if args.meta is not None:
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
                        metavar="absolute file path", 
                        default=None, 
                        help="get the hash value of specified path. (required)")
    # Custom chunk size
    parser.add_argument("-c", "--chunk", 
                        type=int,
                        nargs='?',  
                        metavar="chunk size", 
                        default=1024, 
                        help="file chunks to be processed at a time. (optional)")
    # Save the hash
    parser.add_argument("-s", "--save", 
                        type=str, 
                        nargs='?', 
                        metavar="hash path", 
                        const="hash.txt",
                        default=None, 
                        help="save file hashes at the specified path. (optional)")
    # Generate MetaData
    parser.add_argument("-m", "--meta", 
                        type=str,
                        nargs='?',
                        metavar="meta path",
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
