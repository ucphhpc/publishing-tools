import os

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_DIR = os.path.join(TESTS_DIR, "tmp")

KEY_GENERATOR = "gpg"
GPG_TEST_SIGN_KEYRING = "sign-test-keyring.gpg"
TMP_TEST_GNUPG_DIR = os.path.join(TMP_TEST_DIR, ".gnupg")
GPG_SIGN_COMMON_ARGS = [
    "--homedir",
    TMP_TEST_GNUPG_DIR,
    "--no-default-keyring",
    "--keyring",
    GPG_TEST_SIGN_KEYRING,
    "--no-tty",
    "--batch",
]
GPG_GEN_KEY_ARGS = GPG_SIGN_COMMON_ARGS + ["--quick-gen-key", "--passphrase", ""]
GPG_GET_FINGERPRINT_ARGS = GPG_SIGN_COMMON_ARGS + ["--with-colons", "--fingerprint"]
GPG_SIGN_ARGS = GPG_SIGN_COMMON_ARGS + ["--sign", "--passphrase", ""]
GPG_DELETE_ARGS = GPG_SIGN_COMMON_ARGS + [
    "--delete-secret-and-public-key",
    "--yes",
]
