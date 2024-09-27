import sys
import os
import argparse
from publish.utils.io import exists, remove
from publish.signature import SignatureTypes, sign_file
from publish.cli.common import error_print
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, SIGN_FAILURE

SCRIPT_NAME = __file__


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        help="Path of the file to sign.",
    )
    parser.add_argument("key", help="Path of the key to sign the file with.")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path of the output file. Default is None, which will output to the FILE path with the --sign-command extension.",
    )
    parser.add_argument(
        "--remove-original",
        "-ro",
        action="store_true",
        default=False,
        help="Flag to remove the original file after signing.",
    )
    parser.add_argument(
        "--signature-generator",
        "-sg",
        default=SignatureTypes.GPG.value,
        choices=[SignatureTypes.GPG.value],
        help="Which signaturer to use to sign the file.",
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
    file_ = os.path.realpath(os.path.expanduser(parsed_args.file))
    key = parsed_args.key
    if parsed_args.output:
        output = os.path.realpath(os.path.expanduser(parsed_args.output))
    else:
        output = None
    remove_original = parsed_args.remove_original
    signature_generator = parsed_args.signature_generator
    signature_args = parsed_args.signature_args
    verbose = parsed_args.verbose

    if not exists(file_):
        error_print(f"File to sign not found: {file_}")
        return FILE_NOT_FOUND

    if isinstance(signature_args, str):
        # The underlying API expects a list of arguments
        signature_args = signature_args.split()

    if verbose:
        print(
            f"Signing file: {file_} with key: {key} using signature generator: {signature_generator} with arguments: {signature_args}"
        )

    signed = sign_file(
        file_,
        key,
        output=output,
        sign_command=signature_generator,
        sign_args=signature_args,
        verbose=verbose,
    )
    if not signed:
        error_print(f"Failed to sign file: {file_}")
        return SIGN_FAILURE
    if remove_original:
        if verbose:
            print(f"Removing original file: {file_}")
        if not remove(file_):
            error_print(f"Failed to remove original file: {file_}")
            return SIGN_FAILURE
    if verbose:
        print(f"Successfully signed file: {file_}")
    return SUCCESS


def cli():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
