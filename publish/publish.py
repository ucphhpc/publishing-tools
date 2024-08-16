from enum import StrEnum
from publish.utils.io import exists, copy, write, hashsum
from publish.signature import sign_file, SignatureTypes
from publish.publish_container import container_publish_to_archive


class PublishTypes(StrEnum):
    FILE = "file"
    CONTAINER_IMAGE_ARCHIVE = "container_image_archive"


# TODO add GITHUB and CONTAINER_IMAGE_REGISTRY types


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


def publish(
    source,
    destination,
    publish_type,
    with_checksum=False,
    checksum_algorithm=ChecksumTypes.SHA256,
    with_signature=False,
    signature_generator=SignatureTypes.GPG,
    signature_key=None,
    signauture_args=None,
):
    checksum_input, signature_input = None, None
    if publish_type == PublishTypes.FILE:
        published = file_publish(source, destination)
        if not published:
            return False
        checksum_input = signature_input = destination
    elif publish_type == PublishTypes.CONTAINER_IMAGE_ARCHIVE:
        archived = container_publish_to_archive(source, destination)
        if not archived:
            return False
        checksum_input = signature_input = destination
    else:
        return False

    # Because we need to publish the archive file before we can
    # calculate the checksum and sign it, we need to do it here.
    if with_checksum and checksum_input and exists(checksum_input):
        checksum_file_destination = f"{checksum_input}.{checksum_algorithm}"
        checksum_file = write_checksum_file(
            checksum_input,
            destination=checksum_file_destination,
            algorithm=checksum_algorithm,
        )
        if not checksum_file:
            return False

    if with_signature and signature_input and exists(signature_input):
        if not signature_key:
            return False
        signature_file_destination = f"{signature_input}.{signature_generator}"
        signed_file = sign_file(
            signature_input,
            signature_key,
            sign_command=signature_generator,
            sign_args=signauture_args,
            output=signature_file_destination,
        )
        if not signed_file:
            return False
    return True


def file_publish(source, destination):
    """
    Publishes a file from source to destination by copy.
    The destination can be either a directory or a file.
    """
    if not exists(source):
        return False
    return copy(source, destination)
