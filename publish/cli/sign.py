import sys
import os
import argparse
from publish.signature import SignatureTypes, sign_file
from publish.utils.io import exists
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, SIGN_FAILURE

SCRIPT_NAME = __file__


def parse_args(args):
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "file",
        help="Path to the file to sign.",
    )
    parser.add_argument("key", help="Path to the key to sign the file with.")
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Path to the output file. Default is None, which will output to the FILE path with the --sign-command extension.",
    )
    parser.add_argument(
        "--signature-generator",
        "-sg",
        default=SignatureTypes.GPG,
        choices=[SignatureTypes.GPG],
        help="Which signaturer to use to sign the file.",
    )
    parser.add_argument(
        "--signature-args",
        "-sa",
        default="--sign",
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
    output = parsed_args.output
    signature_generator = parsed_args.signature_generator
    signature_args = parsed_args.signature_args
    verbose = parsed_args.verbose

    if not exists(file_):
        print(f"File to sign not found: {file_}", file=sys.stderr)
        return FILE_NOT_FOUND

    signed = sign_file(
        file_,
        key,
        output=output,
        sign_command=signature_generator,
        sign_args=signature_args,
        verbose=verbose,
    )
    if not signed:
        return SIGN_FAILURE
    return SUCCESS


def cli():
    sys.exit(main(sys.argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
