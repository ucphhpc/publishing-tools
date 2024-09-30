from publish.utils.io import exists, copy
from publish.signature import sign_file, SignatureTypes, SignatureSources
from publish.publish_container import container_publish_to_archive
from publish.checksum import ChecksumTypes, write_checksum_file
from publish.common import StrEnum


class PublishTypes(StrEnum):
    FILE = "file"
    CONTAINER_IMAGE_ARCHIVE = "container_image_archive"


# TODO add GITHUB and CONTAINER_IMAGE_REGISTRY types


def publish(
    source,
    destination,
    publish_type,
    with_checksum=False,
    checksum_algorithm=ChecksumTypes.SHA256,
    with_signature=False,
    signature_source=SignatureSources.SOURCE_INPUT,
    signature_generator=SignatureTypes.GPG,
    signature_key=None,
    signauture_args=None,
    signature_output=None,
    verbose=False,
):
    checksum_input, signature_input = None, None
    if publish_type == PublishTypes.FILE:
        published = file_publish(source, destination)
        if not published:
            return False
        checksum_input = signature_input = destination
    elif publish_type == PublishTypes.CONTAINER_IMAGE_ARCHIVE:
        archived = container_publish_to_archive(source, destination, verbose=verbose)
        if not archived:
            return False
        checksum_input = signature_input = destination
    else:
        return False

    # Because we need to publish the archive file before we can
    # calculate the checksum and sign it, we need to do it here.
    if with_checksum and checksum_input and exists(checksum_input):
        checksum_file_destination = f"{checksum_input}.{checksum_algorithm}"
        if signature_source == SignatureSources.GENERATED_CHECKSUM_FILE:
            signature_input = checksum_file_destination

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

        signed_file = sign_file(
            signature_input,
            signature_key,
            sign_command=signature_generator,
            sign_args=signauture_args,
            output=signature_output,
            verbose=verbose,
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
