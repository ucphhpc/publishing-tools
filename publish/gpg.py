import os
from publish.utils.job import run

# When using the gpg --fingerprint command with --with-colons
# the fingerprint is stored in the 10th field in the output string with the "fpr" prefix
# if you split on the : character
GPG_KEY_FINGERPRINT_SPLIT_CHAR = ":"
GPG_KEY_FINGERPRINT_COLON_PREFIX = "fpr"
GPG_KEY_FINGERPRINT_COLON_INDEX = 9

GPG_VERIFY_OUTPUT_PREFIX = "[GNUPG:] "
GPG_VERIFY_SUCCESS_PREFIX = f"{GPG_VERIFY_OUTPUT_PREFIX}GOODSIG"


def gen_key(
    key_name, key_generator="gpg", key_args=None, verbose=False, **extra_kwargs
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


def get_key_fingerprint(key_name, key_generator="gpg", key_args=None, verbose=False):
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


def delete_key(key_fingerprint, delete_command="gpg", delete_args=None, verbose=False):
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
    file_, key, sign_command="gpg", sign_args=None, output=None, verbose=False
):
    filename = os.path.basename(file_)
    if not output:
        output = f"{filename}.{sign_command}"

    if not sign_args:
        sign_args = ["--no-tty", "--batch", "--sign"]

    if verbose:
        print(
            f"Signing file: {file_} with key: {key} using the command: {sign_command} with arguments: {sign_args} outputting to: {output}"
        )

    sign_job_command = [sign_command, "-u", key, "--output", output]
    sign_job_command.extend(sign_args)
    sign_job_command.append(file_)
    success, result = run(sign_job_command, output_format="str")
    if not success:
        if verbose:
            print(
                f"Failed to sign file: {file_}, output: {result['output']}, error: {result['error']}"
            )
        return False
    return True


def verify_file(file_, key, verify_command="gpg", verify_args=None, verbose=False):
    execute_command = [verify_command]
    if not verify_args:
        verify_args = [
            "--no-tty",
            "--batch",
            "--status-fd",
            "0",
            "--with-colons",
            "--verify",
        ]
    execute_command.extend(verify_args)
    if not verbose:
        execute_command.append("--quiet")
    execute_command.extend(["-u", key])
    execute_command.append(file_)

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
                print(f"Successfully verified file: {file_} with key: {key}")
            return True
    if verbose:
        print(f"Successfully verified file: {file_} with key: {key}")
    return True
