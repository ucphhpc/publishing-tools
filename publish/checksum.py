import hashlib
from publish.utils.io import load


def get_checksum(path, algorithm="sha256", checksum_header=65536):
    content = load(path, mode="rb")
    if not content:
        return None
    if algorithm not in hashlib.algorithms_available:
        return None

    hasher = hashlib.new(algorithm)
    hasher.update(content)
    return hasher.hexdigest()
