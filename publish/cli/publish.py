import argparse
import sys
import os
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
    verbose = parsed_args.verbose

    if not exists(file_):
        print(f"File to publish not found: {file_}", file=sys.stderr)
        return FILE_NOT_FOUND
    if verbose:
        print(f"Publishing file: {file_}")
    # TODO: incorporate the publish logic here

    return SUCCESS


def cli():
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
