import os
from publish.utils.job import run
from publish.common import StrEnum


class SignatureTypes(StrEnum):
    GPG = "gpg"


class SignatureSources(StrEnum):
    SOURCE_INPUT = "source_input"
    GENERATED_CHECKSUM_FILE = "generated_checksum_file"


# When using the gpg --fingerprint command with --with-colons
# the fingerprint is stored in the 10th field in the output string with the "fpr" prefix
# if you split on the : character
GPG_KEY_FINGERPRINT_SPLIT_CHAR = ":"
GPG_KEY_FINGERPRINT_COLON_PREFIX = "fpr"
GPG_KEY_FINGERPRINT_COLON_INDEX = 9

GPG_VERIFY_OUTPUT_PREFIX = "[GNUPG:] "
GPG_VERIFY_SUCCESS_PREFIX = f"{GPG_VERIFY_OUTPUT_PREFIX}GOODSIG"


def gen_key(
    key_name,
    key_generator=SignatureTypes.GPG,
    key_args=None,
    verbose=False,
    **extra_kwargs,
):
    gen_command = [
        key_generator,
    ]
    if not key_args:
        key_args = [
            "--no-tty",
            "--batch",
        ]
    gen_command.extend(key_args)
    if not verbose:
        gen_command.append("--quiet")

    gen_command.append(key_name)
    success, result = run(gen_command, output_format="str")
    if not success:
        if verbose:
            print(
                f"Failed to generate key: {key_name}, output: {result['output']}, error: {result['error']}"
            )
        return False
    # Extract unique fingerprint from the key generation output
    return True


def get_key_fingerprint(
    key_name, key_generator=SignatureTypes.GPG, key_args=None, verbose=False
):
    fingerprint_command = [key_generator]
    if not key_args:
        key_args = [
            "--batch",
            "--with-colons",
            "--fingerprint",
        ]
    if "--with-colons" not in key_args:
        raise ValueError(
            "get_key_fingerprint requires the '--with-colons' argument as a `key_args' to parse and extract the fingerprint from gpg"
        )
    if "--fingerprint" not in key_args:
        raise ValueError(
            "get_key_fingerprint requires the '--fingerprint' argument as a `key_args' to parse and extract the fingerprint"
        )

    fingerprint_command.extend(key_args)
    if not verbose:
        fingerprint_command.append("--quiet")
    fingerprint_command.append(key_name)

    success, result = run(fingerprint_command, output_format="str")
    if not success:
        if verbose:
            print(
                f"Failed to get key fingerprint: {key_name}, output: {result['output']}, error: {result['error']}"
            )
        return None
    fingerprint = None
    for line in result["output"].split("\n"):
        if (
            line.startswith(GPG_KEY_FINGERPRINT_COLON_PREFIX)
            and GPG_KEY_FINGERPRINT_SPLIT_CHAR in line
        ):
            fingerprint = line.split(GPG_KEY_FINGERPRINT_SPLIT_CHAR)[
                GPG_KEY_FINGERPRINT_COLON_INDEX
            ]
            break
    return fingerprint


def delete_key(
    key_fingerprint, delete_command=SignatureTypes.GPG, delete_args=None, verbose=False
):
    del_command = [
        delete_command,
    ]
    if not delete_args:
        delete_args = [
            "--no-tty",
            "--delete-secret-and-public-key",
            "--yes",
            "--batch",
        ]
    if "--delete-secret-and-public-key" not in delete_args:
        raise ValueError(
            "delete_key requires the '--delete-secret-and-public-key' argument as a `delete_args' to delete the key from gpg"
        )
    del_command.extend(delete_args)
    if not verbose:
        del_command.append("--quiet")
    del_command.append(key_fingerprint)
    success, result = run(del_command, output_format="str")
    if not success:
        if verbose:
            print(
                f"Failed to delete key: {key_fingerprint}, output: {result['output']}, error: {result['error']}"
            )
        return False
    return True


def sign_file(
    file_,
    key_name,
    sign_command=SignatureTypes.GPG,
    sign_args=None,
    output=None,
    verbose=False,
):
    if not output:
        filename = os.path.basename(file_)
        directory = os.path.dirname(file_)
        output = os.path.join(directory, f"{filename}.{sign_command}")

    if not sign_args:
        # https://www.gnupg.org/documentation/manuals/gnupg24/gpg.1.html
        # Recommended by gpg to use the --batch, --status-fd, --with-colons flags when another
        # piece of software is interfacing with gpg.
        sign_args = [
            "--no-tty",
            "--status-fd",
            "0",
            "--with-colons",
            "--batch",
            "--sign",
        ]

    if verbose:
        print(
            f"Signing file: {file_} with key: {key_name} using the command: {sign_command} with arguments: {sign_args} outputting to: {output}"
        )

    sign_job_command = [sign_command, "-u", key_name, "--output", output]
    if sign_args:
        sign_job_command.extend(sign_args)
    sign_job_command.append(file_)
    if verbose:
        print(f"Executing signing command: {' '.join(sign_job_command)}")
    success, result = run(sign_job_command, output_format="str")
    if not success:
        if verbose:
            print(
                f"Failed to sign file: {file_}, output: {result['output']} error: {result['error']}"
            )
        return False
    return True


def verify_file(
    file_,
    key_name,
    verify_command=SignatureTypes.GPG,
    verify_args=None,
    verify_additional_files=None,
    verbose=False,
):
    """
    Verify a file with a key using SignatureTypes.GPG by default.
    If the file is successfully verified, return True, otherwise return False.

    Note:
    gpg will try to use every available public key in the selected keyring
    after the specified `key_name`. Therefore if the file is signed with any key
    that is in the selected public keyring, the file will be verified successfully.
    """
    if not verify_args:
        verify_args = [
            "--no-tty",
            "--batch",
            "--status-fd",
            "0",
            "--with-colons",
            "--verify",
        ]

    if not verify_additional_files:
        verify_additional_files = []

    execute_command = [verify_command]
    execute_command.extend(verify_args)
    if not verbose:
        execute_command.append("--quiet")
    execute_command.extend(["-u", key_name])
    execute_command.append(file_)
    execute_command.extend(verify_additional_files)

    if verbose:
        print(f"Executing command: {execute_command}")

    success, result = run(execute_command, output_format="str")
    if not success:
        if verbose:
            print(
                f"Failed to verify file: {file_}, output: {result['output']}, error: {result['error']}"
            )
        return False
    for line in result["output"].split("\n"):
        if line.startswith(GPG_VERIFY_SUCCESS_PREFIX):
            if verbose:
                print(f"Successfully verified file: {file_} with key: {key_name}")
            return True
    if verbose:
        print(f"Successfully verified file: {file_} with key: {key_name}")
    return True
