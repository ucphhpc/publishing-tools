import argparse
import sys
import os
from publish.publish import PublishTypes, publish, ChecksumTypes
from publish.signature import sign_file
from publish.utils.io import exists
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, PUBLISH_FAILURE

SCRIPT_NAME = __file__


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        help="Path to the file to publish.",
    )
    parser.add_argument(
        "destination", help="Path to the destination to publish the file to."
    )
    parser.add_argument(
        "--publish-type",
        "-pt",
        default=PublishTypes.FILE,
        choices=[PublishTypes.FILE],
    )
    parser.add_argument(
        "--with-checksum",
        "-wc",
        action="store_true",
        default=False,
        help="Whether to also publish a checksum file.",
    )
    parser.add_argument(
        "--checksum-algorithm",
        "-ca",
        default=ChecksumTypes.SHA256,
        choices=[ChecksumTypes.SHA256, ChecksumTypes.SHA512, ChecksumTypes.MD5],
        help="Algorithm to use for the checksum.",
    )
    parser.add_argument(
        "--with-signature",
        "-ws",
        action="store_true",
        default=False,
        help="Whether to also publish a signed file.",
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
    file_ = os.path.realpath(os.path.expanduser(parsed_args.file))
    destination = parsed_args.destination
    with_checksum = parsed_args.with_checksum
    with_signature = parsed_args.with_signature
    verbose = parsed_args.verbose

    if not exists(file_):
        print(f"File to publish not found: {file_}", file=sys.stderr)
        return FILE_NOT_FOUND
    if verbose:
        print(f"Publishing file: {file_} to destination: {destination}")

    if not publish(
        file_,
        destination,
        PublishTypes.FILE,
        with_checksum=with_checksum,
        with_signature=with_signature,
    ):
        return PUBLISH_FAILURE

    return SUCCESS


def cli():
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
