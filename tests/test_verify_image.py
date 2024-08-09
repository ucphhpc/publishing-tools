import os
import unittest

import tests.base
from publish.gpg import gen_key, delete_key, get_key_fingerprint, verify_file, sign_file
from publish.utils.io import makedirs, exists, remove, write

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_DIR = os.path.join(CURRENT_DIR, "tmp", "test_verify")
TMP_TEST_GNUPG_DIR = os.path.join(TMP_TEST_DIR, ".gnupg")
TMP_TEST_VERIFY_FILE = os.path.join(TMP_TEST_DIR, "test_verify_file")
TEST_VERIFY_CONTENT = "foo bar baz"

KEY_GENERATOR = "gpg"
TEST_KEY_NAME = "test_verify_key"
# Used for wrong gpg keychain tests
GPP_WRONG_KEYCHAIN = "wrong-keyring.gpg"
GPG_COMMON_WRONG_KEYCHAIN_ARGS = [
    "--homedir",
    TMP_TEST_GNUPG_DIR,
    "--no-default-keyring",
    "--keyring",
    GPP_WRONG_KEYCHAIN,
    "--no-tty",
    "--batch",
]
# Regular custom gpg keychain tests
GPG_TEST_VERIFY_KEYRING = "verify-test-keyring.gpg"
GPG_COMMON_ARGS = [
    "--homedir",
    TMP_TEST_GNUPG_DIR,
    "--no-default-keyring",
    "--keyring",
    GPG_TEST_VERIFY_KEYRING,
    "--no-tty",
    "--batch",
]
GPG_GEN_KEY_ARGS = GPG_COMMON_ARGS + [
    "--quick-gen-key",
    "--passphrase",
    "",
]
GPG_GET_FINTERPRINT_ARGS = GPG_COMMON_ARGS + [
    "--with-colons",
    "--fingerprint",
]
GPG_DELETE_ARGS = GPG_COMMON_ARGS + [
    "--delete-secret-and-public-key",
    "--yes",
]
GPG_SIGN_ARGS = GPG_COMMON_ARGS + [
    "--sign",
    "--passphrase",
    "",
]
GPG_VERIFY_ARGS = GPG_COMMON_ARGS + [
    "--with-colons",
    "--verify",
]
GPG_VERIFY_WRONG_KEYCHAIN_ARGS = GPG_COMMON_WRONG_KEYCHAIN_ARGS + [
    "--with-colons",
    "--verify",
]


class TestGpGVerifyFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the temporary test files to sign
        if not exists(TMP_TEST_DIR):
            assert makedirs(TMP_TEST_DIR) is True
        # Gen sign test key
        assert (
            gen_key(
                TEST_KEY_NAME,
                key_generator=KEY_GENERATOR,
                key_args=GPG_GEN_KEY_ARGS,
            )
            is True
        )
        cls.key_fingerprint = get_key_fingerprint(
            TEST_KEY_NAME,
            key_generator=KEY_GENERATOR,
            key_args=GPG_GET_FINTERPRINT_ARGS,
        )
        assert cls.key_fingerprint is not None
        assert write(TMP_TEST_VERIFY_FILE, TEST_VERIFY_CONTENT) is True

    @classmethod
    def tearDownClass(cls):
        # Delete the class test key
        assert (
            delete_key(
                cls.key_fingerprint,
                delete_command=KEY_GENERATOR,
                delete_args=GPG_DELETE_ARGS,
            )
            is True
        )
        # Remove the temporary directory and its contents
        assert remove(TMP_TEST_DIR, recursive=True) is True
        assert exists(TMP_TEST_DIR) is False

    def test_verify_failure(self):
        # Verify a file that has not been signed
        self.assertFalse(
            verify_file(
                TMP_TEST_VERIFY_FILE,
                TEST_KEY_NAME,
                verify_command=KEY_GENERATOR,
                verify_args=GPG_VERIFY_ARGS,
            )
        )

    def test_sign_with_nonexisting_key(self):
        non_existing_key = "non_existing_key"
        # Sign the file with a non-existing key
        output_signed_file = (
            f"{TMP_TEST_VERIFY_FILE}-{non_existing_key}.{KEY_GENERATOR}"
        )
        self.assertFalse(
            sign_file(
                TMP_TEST_VERIFY_FILE,
                non_existing_key,
                sign_command=KEY_GENERATOR,
                sign_args=GPG_SIGN_ARGS,
                output=output_signed_file,
            )
        )
        self.assertFalse(exists(output_signed_file))

    def test_verify_success(self):
        # Sign the file to verify
        output_signed_file = f"{TMP_TEST_VERIFY_FILE}.{KEY_GENERATOR}"
        self.assertTrue(
            sign_file(
                TMP_TEST_VERIFY_FILE,
                TEST_KEY_NAME,
                sign_command=KEY_GENERATOR,
                sign_args=GPG_SIGN_ARGS,
                output=output_signed_file,
            )
        )
        self.assertTrue(
            verify_file(
                output_signed_file,
                TEST_KEY_NAME,
                verify_command=KEY_GENERATOR,
                verify_args=GPG_VERIFY_ARGS,
            )
        )
        self.assertTrue(remove(output_signed_file))

    def test_verify_failure_wrong_keychain(self):
        # Sign the file to verify
        wrong_keychain = "wrong_keychain"
        output_signed_file = f"{TMP_TEST_VERIFY_FILE}-{wrong_keychain}.{KEY_GENERATOR}"
        self.assertTrue(
            sign_file(
                TMP_TEST_VERIFY_FILE,
                TEST_KEY_NAME,
                sign_command=KEY_GENERATOR,
                sign_args=GPG_SIGN_ARGS,
                output=output_signed_file,
            )
        )
        # Verify the signed file with a different key
        self.assertFalse(
            verify_file(
                output_signed_file,
                TEST_KEY_NAME,
                verify_command=KEY_GENERATOR,
                verify_args=GPG_VERIFY_WRONG_KEYCHAIN_ARGS,
            )
        )
        self.assertTrue(remove(output_signed_file))
