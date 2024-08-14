import sys
import os
import argparse
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, VERIFY_FAILURE
from publish.utils.io import exists
from publish.signature import SignatureTypes, verify_file


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
    verbose = parsed_args.verbose

    if not exists(file_):
        print(f"File to verify not found: {file_}", file=sys.stderr)
        return FILE_NOT_FOUND

    verified = verify_file(file_, key, verify_command, verify_args, verbose=verbose)
    if not verified:
        return VERIFY_FAILURE
    return SUCCESS


def cli():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
