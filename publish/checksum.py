from publish.utils.io import hashsum, write, exists, load
from publish.common import StrEnum


class ChecksumTypes(StrEnum):
    SHA256 = "sha256"
    SHA512 = "sha512"
    MD5 = "md5"


def checksum_file(path, algorithm=ChecksumTypes.SHA256):
    if not exists(path):
        return False
    return hashsum(path, algorithm=algorithm)


def write_checksum_file(path, destination=None, algorithm=ChecksumTypes.SHA256):
    checksum = checksum_file(path, algorithm=algorithm)
    if not checksum:
        return False
    if not destination:
        return write(path + f".{algorithm}", checksum)
    return write(destination, checksum)


def checksum_equal(path, checksum_file_path, algorithm=ChecksumTypes.SHA256):
    checksum = checksum_file(path, algorithm=algorithm)
    if not checksum:
        return False
    return checksum == load(checksum_file_path)
