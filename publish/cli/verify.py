import sys
import os
import argparse
from publish.cli.return_codes import (
    SUCCESS,
    FILE_NOT_FOUND,
    VERIFY_FAILURE,
    CHECKSUM_FAILURE,
)
from publish.utils.io import exists
from publish.signature import SignatureTypes, verify_file
from publish.checksum import ChecksumTypes, checksum_equal


SCRIPT_NAME = __file__


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        help="Path to the file to verify",
    )
    parser.add_argument("key", help="Path to the key to verify the file with")
    parser.add_argument(
        "--verify-command",
        "-vc",
        default=SignatureTypes.GPG,
        choices=[SignatureTypes.GPG],
        help="Command to verify the file with. Default is 'gpg'.",
    )
    # https://www.gnupg.org/documentation/manuals/gnupg24/gpg.1.html
    # Recommended by gpg to use the --batch, --status-fd, --with-colons flags when another
    # piece of software is interfacing with gpg.
    parser.add_argument(
        "--verify-args",
        "-va",
        default="--verify --batch --status-fd 0 --with-colons",
        help="Additional arguments to pass to the verify command.",
    )
    parser.add_argument(
        "--with-checksum",
        "-wc",
        action="store_true",
        default=False,
        help="Whether to also verify a checksum file.",
    )
    parser.add_argument(
        "--checksum-file",
        "-cf",
        default=None,
        help="""
        Path to the checksum file to verify against when --with-checksum is enabled.
        If none is provided, the checksum file will be assumed to be in the same directory as the file to verify with the same name and the checksum file extension.
        """,
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
        help="Which checksum algorithm to use for verification when --with-checksum is enabled.",
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
    key = parsed_args.key
    verify_command = parsed_args.verify_command
    verify_args = parsed_args.verify_args
    with_checksum = parsed_args.with_checksum
    checksum_algorithm = parsed_args.checksum_algorithm
    checksum_file = parsed_args.checksum_file
    verbose = parsed_args.verbose

    if not exists(file_):
        print(f"File to verify not found: {file_}", file=sys.stderr)
        return FILE_NOT_FOUND

    if with_checksum:
        if not checksum_file:
            # Try to discover the checksum file in the same directory as the file to verify
            # since the user did not provide one.
            checksum_file = f"{file_}.{checksum_algorithm}"
            if not exists(checksum_file):
                print(f"Checksum file not found: {checksum_file}", file=sys.stderr)
                return FILE_NOT_FOUND

        if not checksum_equal(file_, checksum_file, algorithm=checksum_algorithm):
            print(
                f"Checksum verification failed for file: {file_} with checksum file: {checksum_file}",
                file=sys.stderr,
            )
            return CHECKSUM_FAILURE

    if isinstance(verify_args, str):
        # The underlying API expects a list of arguments
        verify_args = verify_args.split()

    verified = verify_file(file_, key, verify_command, verify_args, verbose=verbose)
    if not verified:
        return VERIFY_FAILURE
    return SUCCESS


def cli():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
