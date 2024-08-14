import argparse
import sys
import os
from publish.publish import PublishTypes
from publish.signature import sign_file
from publish.utils.io import exists
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND

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
        "--checksum-file",
        "-cf",
        default=None,
        help="Path to the checksum file to also publish.",
    )
    parser.add_argument(
        "--signed-file",
        "-sf",
        default=None,
        help="Path to the signed file to also publish.",
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
    checksum_file = parsed_args.checksum_file
    signed_file = parsed_args.signed_file
    verbose = parsed_args.verbose

    if not exists(file_):
        print(f"File to publish not found: {file_}", file=sys.stderr)
        return FILE_NOT_FOUND
    if verbose:
        print(f"Publishing file: {file_} to destination: {destination}")

    return SUCCESS


def cli():
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
