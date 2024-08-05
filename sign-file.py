import sys
import os
import argparse
from utils.job import run


SCRIPT_NAME = __file__
SUCCESS = 0
FILE_NOT_FOUND = 1
SIGN_FAILURE = 2


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

    if not os.path.exists(file_):
        if verbose:
            print(f"File to sign not found: {file_}")
        return FILE_NOT_FOUND

    filename = os.path.basename(file_)
    if not output:
        output = f"{filename}.{sign_command}"

    formatted_sign_args = sign_args.split()
    if verbose:
        print(
            f"Signing file: {file_} with key: {key} using the command: {sign_command} with arguments: {formatted_sign_args} outputting to: {output}"
        )

    sign_job_command = [sign_command, "-u", key, "--output", output, file_]
    sign_job_command.extend(formatted_sign_args)
    success, result = run(sign_job_command, output_format="str")
    if not success:
        if verbose:
            print(
                f"Failed to sign file: {file_}, output: {result['output']}, error: {result['error']}"
            )
        return SIGN_FAILURE
    return SUCCESS


if __name__ == "__main__":
    sys.exit(main())
