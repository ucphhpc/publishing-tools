import sys
import os
import argparse
from utils.job import run


SCRIPT_NAME = __file__
SUCCESS = 0
FILE_NOT_FOUND = 1
VERIFY_FAILURE = 2


def main():
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
        default="gpg",
        help="Command to verify the file with. Default is 'gpg'.",
    )
    parser.add_argument(
        "--verify-args",
        "-va",
        default="--verify",
        help="Additional arguments to pass to the verify command.",
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
    verify_command = args.verify_command
    verify_args = args.verify_args
    verbose = args.verbose

    if not os.path.exists(file_):
        if verbose:
            print(f"File to verify not found: {file_}")
        return FILE_NOT_FOUND

    verify_command = [verify_command, verify_args, "-u", key, file_]

    success, result = run(verify_command, output_format="str")
    if not success:
        if verbose:
            print(
                f"Failed to verify file: {file_}, output: {result['output']}, error: {result['error']}"
            )
        return VERIFY_FAILURE
    if verbose:
        print(f"Successfully verified file: {file_} with key: {key}")
    print(f"{result}")
    return SUCCESS


if __name__ == "__main__":
    sys.exit(main())
