import sys
import os
import argparse
from publish.gpg import sign_file
from publish.utils.io import exists
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, SIGN_FAILURE

SCRIPT_NAME = __file__


def main():
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        help="Path to the file to sign",
    )
    parser.add_argument("key", help="Path to the key to sign the file with")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path to the output file. Default is None, which will output to the FILE path with the --sign-command extension.",
    )
    parser.add_argument(
        "--sign-command",
        "-s",
        default="gpg",
        help="Command to sign the file with. Default is 'gpg'.",
    )
    parser.add_argument(
        "--sign-args",
        "-a",
        default="--sign",
        help="Additional arguments to pass to the sign command.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Flag to enable verbose output.",
    )
    args = parser.parse_args()

    file_ = os.path.realpath(os.path.expanduser(args.file))
    key = args.key
    output = args.output
    sign_command = args.sign_command
    sign_args = args.sign_args
    verbose = args.verbose

    if not exists(file_):
        if verbose:
            print(f"File to sign not found: {file_}")
        return FILE_NOT_FOUND

    signed = sign_file(file_, key, output, sign_command, sign_args, verbose=verbose)
    if not signed:
        return SIGN_FAILURE
    return SUCCESS


def cli():
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
