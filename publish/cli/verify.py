import sys
import os
import argparse
from publish.utils.io import exists
from publish.signature import SignatureTypes, verify_file
from publish.checksum import ChecksumTypes, checksum_equal
from publish.cli.common import error_print
from publish.cli.return_codes import (
    SUCCESS,
    FILE_NOT_FOUND,
    VERIFY_FAILURE,
    CHECKSUM_FAILURE,
)

SCRIPT_NAME = __file__


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        help="Path of the file to verify.",
    )
    parser.add_argument(
        "key",
        help="The key that the --verify-command should use to verify the file with.",
    )
    parser.add_argument(
        "--verify-with-additional-files",
        "-vwaf",
        nargs="+",
        default=[],
        help="Additional files to verify with the key. This is useful when verifying a detached signature.",
    )
    parser.add_argument(
        "--verify-command",
        "-vc",
        default=SignatureTypes.GPG.value,
        choices=[SignatureTypes.GPG.value],
        help="Command to verify the file with.",
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
        "--checksum-digest-file",
        "-cdf",
        default=None,
        help="""
        Path of the file containing the digest to validate against when --with-checksum is enabled.
        If none is provided, the checksum file will be assumed to be in the same directory as the verify file with the same base name and the selected --checksum-algorithm extension.
        """,
    )
    parser.add_argument(
        "--checksum-original-file",
        "-cof",
        default=None,
        help="""
        Path of the file to validate the --checksum-digest-file content against when --with-checksum is enabled.
        """,
    )
    parser.add_argument(
        "--checksum-algorithm",
        "-ca",
        default=ChecksumTypes.SHA256.value,
        choices=[
            ChecksumTypes.SHA256.value,
            ChecksumTypes.SHA512.value,
            ChecksumTypes.MD5.value,
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


def search_for_file(path, search_priorities, verbose=False):
    for option in search_priorities:
        if exists(option):
            return option
    return None


def main(args):
    parsed_args = parse_args(args)
    file_ = os.path.realpath(os.path.expanduser(parsed_args.file))
    key = parsed_args.key
    verify_additional_files = [
        os.path.expanduser(path) for path in parsed_args.verify_with_additional_files
    ]
    verify_command = parsed_args.verify_command
    verify_args = parsed_args.verify_args
    with_checksum = parsed_args.with_checksum
    checksum_algorithm = parsed_args.checksum_algorithm
    if parsed_args.checksum_digest_file:
        checksum_digest_file = os.path.realpath(
            os.path.expanduser(parsed_args.checksum_digest_file)
        )
    else:
        checksum_digest_file = None
    if parsed_args.checksum_original_file:
        checksum_original_file = os.path.realpath(
            os.path.expanduser(parsed_args.checksum_original_file)
        )
    else:
        checksum_original_file = None
    verbose = parsed_args.verbose

    if not exists(file_):
        error_print(f"The file to verify was not found: {file_}")
        return FILE_NOT_FOUND

    if verify_additional_files:
        for additional_file in verify_additional_files:
            if not exists(additional_file):
                error_print(
                    f"Additional file to use for verification is not found: {additional_file}"
                )
                return FILE_NOT_FOUND

    if with_checksum:
        if not checksum_original_file:
            # Try to discover the original file in the same directory as the file to verify
            # since the user did not provide one.
            search_priorities = [
                file_.strip(f".{verify_command}"),
            ]
            checksum_original_file = search_for_file(
                file_, search_priorities, verbose=verbose
            )
            if not checksum_original_file or not exists(checksum_original_file):
                error_print(
                    "No original file provided to validate the checksum digest against."
                )
                return FILE_NOT_FOUND

        if not checksum_digest_file:
            # Try to discover the checksum digest file in the same directory as the file to verify
            # since the user did not provide one.
            if verbose:
                print(
                    "The Checksum digest file has not been set by the user, attempting to search for one."
                )
            search_priority = [
                f"{checksum_original_file}.{checksum_algorithm}",
                f"{file_}.{checksum_algorithm}",
            ]
            checksum_digest_file = search_for_file(
                file_, search_priority, verbose=verbose
            )
            if not checksum_digest_file or not exists(checksum_digest_file):
                error_print(
                    "Failed to find a checksum digest file to validate against."
                )
                return FILE_NOT_FOUND
        if not checksum_equal(
            checksum_original_file, checksum_digest_file, algorithm=checksum_algorithm
        ):
            error_print(
                f"Checksum verification failed for file: {checksum_original_file} with checksum file: {checksum_digest_file}"
            )
            return CHECKSUM_FAILURE

    if isinstance(verify_args, str):
        # The underlying API expects a list of arguments
        verify_args = verify_args.split()

    verified = verify_file(
        file_,
        key,
        verify_command,
        verify_args,
        verify_additional_files=verify_additional_files,
        verbose=verbose,
    )
    if not verified:
        error_print(f"Failed to verify file: {file_}")
        return VERIFY_FAILURE
    if verbose:
        print(f"Successfully verified file: {file_}")
    return SUCCESS


def cli():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
