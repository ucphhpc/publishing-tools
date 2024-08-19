import argparse
import sys
import os
from publish.signature import SignatureTypes
from publish.publish import PublishTypes, publish, ChecksumTypes
from publish.publish_container import get_image
from publish.utils.io import exists
from publish.cli.return_codes import (
    SUCCESS,
    FILE_NOT_FOUND,
    IMAGE_NOT_FOUND,
    PUBLISH_FAILURE,
)

SCRIPT_NAME = __file__


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "source",
        help="The source input to publish.",
    )
    parser.add_argument(
        "destination",
        help="Path to the destination to publish to, can be either a directory .",
    )
    parser.add_argument(
        "--publish-type",
        "-pt",
        default=PublishTypes.FILE,
        choices=[PublishTypes.FILE, PublishTypes.CONTAINER_IMAGE_ARCHIVE],
    )
    parser.add_argument(
        "--with-checksum",
        "-wc",
        action="store_true",
        default=False,
        help="Whether to also publish a checksum file in the destination directory.",
    )
    parser.add_argument(
        "--checksum-algorithm",
        "-ca",
        default=ChecksumTypes.SHA256,
        choices=[
            ChecksumTypes.SHA256,
            ChecksumTypes.SHA512,
            ChecksumTypes.MD5,
        ],
        help="Which checksum algorithm to use when --with-checksum is enabled.",
    )
    parser.add_argument(
        "--with-signature",
        "-ws",
        action="store_true",
        default=False,
        help="Whether to also publish a signed edition of the source to the specified destination directory.",
    )
    parser.add_argument(
        "--signature-generator",
        "-sg",
        default=SignatureTypes.GPG,
        choices=[SignatureTypes.GPG],
        help="Which signaturer to use when --with-signature is enabled.",
    )
    parser.add_argument(
        "--signature-key",
        "-sk",
        default=None,
        help="Which key should be used to sign with when --with-signature is enabled.",
    )
    parser.add_argument(
        "--signature-args",
        "-sa",
        default="--sign --batch",
        help="Optional arguments to give the selected --signature-generator.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Flag to enable verbose output.",
    )
    return parser.parse_args(args=args)


def main(args):
    parsed_args = parse_args(args)
    source = parsed_args.source
    destination = parsed_args.destination
    publish_type = parsed_args.publish_type
    with_checksum = parsed_args.with_checksum
    checksum_algorithm = parsed_args.checksum_algorithm
    with_signature = parsed_args.with_signature
    signature_generator = parsed_args.signature_generator
    signature_key = parsed_args.signature_key
    signature_args = parsed_args.signature_args
    verbose = parsed_args.verbose

    if publish_type == PublishTypes.FILE:
        file_path = os.path.realpath(os.path.expanduser(source))
        if not exists(file_path):
            print(f"File to publish not found: {file_path}", file=sys.stderr)
            return FILE_NOT_FOUND
        else:
            source = file_path

    if publish_type == PublishTypes.CONTAINER_IMAGE_ARCHIVE and not get_image(source):
        print(f"Container image to publish not found: {source}", file=sys.stderr)
        return IMAGE_NOT_FOUND

    if with_signature and not signature_key:
        print(
            f"Failed to publish source: {source} with signature, no signature key provided. Please provide one via the --signature-key argument.",
            file=sys.stderr,
        )
        return PUBLISH_FAILURE

    if isinstance(signature_args, str):
        # The underlying API expects a list of arguments
        signature_args = signature_args.split()

    if verbose:
        print(f"Publishing source: {source} to destination: {destination}")

    if not publish(
        source,
        destination,
        publish_type,
        with_checksum=with_checksum,
        checksum_algorithm=checksum_algorithm,
        with_signature=with_signature,
        signature_generator=signature_generator,
        signature_key=signature_key,
        signauture_args=signature_args,
        verbose=verbose,
    ):
        print(
            f"Failed to correctly publish source: {source} to destination: {destination}",
            file=sys.stderr,
        )
        return PUBLISH_FAILURE
    return SUCCESS


def cli():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
