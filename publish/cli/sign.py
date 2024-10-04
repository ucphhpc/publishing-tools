import sys
import os
import argparse
from publish.utils.io import exists
from publish.signature import SignatureTypes, sign_file, write_signature_key_file
from publish.cli.common import error_print
from publish.cli.return_codes import (
    SUCCESS,
    FILE_NOT_FOUND,
    SIGN_FAILURE,
    SIGN_KEY_FILE_FAILURE,
)

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
        "--with-signature-key-output",
        "-wsko",
        action="store_true",
        default=False,
        help="Flag on whether the 'key' used to sign 'file' should be generated.",
    )
    parser.add_argument(
        "--signature-key-output-path",
        "-skop",
        default=None,
        help="The path to where the --with-signature-key-output should be written. If None is set, the default is the same path as the 'file' with an `.asc` extension.",
    )
    parser.add_argument(
        "--signature-key-output-args",
        "-skoa",
        default="--armor --export",
        help="Optional arguments to give the selected --signature-generator when generating the key.",
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
    signature_generator = parsed_args.signature_generator
    signature_args = parsed_args.signature_args
    with_signature_key_output = parsed_args.with_signature_key_output
    signature_key_output_path = parsed_args.signature_key_output_path
    signature_key_output_args = parsed_args.signature_key_output_args
    verbose = parsed_args.verbose

    if not exists(file_):
        error_print(f"File to sign not found: {file_}")
        return FILE_NOT_FOUND

    if isinstance(signature_args, str):
        # The underlying API expects a list of arguments
        signature_args = signature_args.split()

    if isinstance(signature_key_output_args, str):
        # The underlying API expects a list of arguments
        signature_key_output_args = signature_key_output_args.split()

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
    if with_signature_key_output:
        if not signature_key_output_path:
            signature_key_output_path = f"{file_}.asc"
        if verbose:
            print(
                f"Writing signature key to file: {signature_key_output_path} with signature generator: {signature_generator} with arguments: {signature_args}"
            )
        if not write_signature_key_file(
            key,
            signature_key_output_path,
            sign_command=signature_generator,
            sign_args=signature_key_output_args,
            verbose=verbose,
        ):
            error_print(f"Failed to write signature key to file: {key}")
            return SIGN_KEY_FILE_FAILURE
    if verbose:
        print(f"Successfully signed file: {file_}")
    return SUCCESS


def cli():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
