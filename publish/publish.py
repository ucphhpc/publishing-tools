from publish.utils.io import exists, copy, write
from publish.checksum import get_checksum
from publish.signature import sign_file, SignatureTypes


class PublishTypes:
    FILE = "file"
    CONTAINER_REGISTRY = "container_registry"
    GITHUB = "github"


def checksum_file(path, algorithm="sha256"):
    if not exists(path):
        return False
    return get_checksum(path, algorithm=algorithm)


def write_checksum_file(path, destination=None, algorithm="sha256"):
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
    checksum_algorithm="sha256",
    with_signature=False,
    signature_generator=SignatureTypes.GPG,
    signature_key=None,
    signauture_args=None,
):
    if with_checksum:
        if publish_type == PublishTypes.FILE:
            checksum_file_destination = f"{destination}.{checksum_algorithm}"
            checksum_file = write_checksum_file(
                source,
                destination=checksum_file_destination,
                algorithm=checksum_algorithm,
            )
            if not checksum_file:
                return False

    if with_signature:
        if publish_type == PublishTypes.FILE:
            if not signature_key:
                return False
            signature_file_destination = f"{destination}.{signature_generator}"
            signed_file = sign_file(
                source,
                signature_key,
                sign_command=signature_generator,
                sign_args=signauture_args,
                output=signature_file_destination,
            )
            if not signed_file:
                return False

    if publish_type == PublishTypes.FILE:
        return file_publish(source, destination)
    elif publish_type == PublishTypes.CONTAINER_REGISTRY:
        return container_registry_publish(source, destination)
    elif publish_type == PublishTypes.GITHUB:
        return github_publish(source, destination)
    return False


def file_publish(source, destination):
    if not exists(source):
        return False
    return copy(source, destination)


def container_registry_publish(source, destination):
    pass


def github_publish(source, destination):
    pass
