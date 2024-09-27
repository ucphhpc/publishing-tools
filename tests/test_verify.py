import os
import unittest

from publish.signature import (
    gen_key,
    delete_key,
    get_key_fingerprint,
    verify_file,
    sign_file,
    SignatureTypes,
)
from publish.utils.io import makedirs, exists, remove, write
from tests.common import TMP_TEST_PATH, TEST_CONTENT

TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)
TEST_KEY_NAME = f"{TEST_NAME}_key"

# GPG settings
TMP_TEST_GNUPG_DIR = os.path.join(CURRENT_TEST_DIR, ".gnupg")
# Used for wrong gpg keychain tests
GPP_WRONG_KEYCHAIN = f"wrong-keyring.{SignatureTypes.GPG}"
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
GPG_TEST_VERIFY_KEYRING = f"verify-test-keyring.{SignatureTypes.GPG}"
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
GPG_DETACH_SIGN_ARGS = GPG_COMMON_ARGS + ["--detach-sign", "--passphrase", ""]
GPG_VERIFY_ARGS = GPG_COMMON_ARGS + [
    "--with-colons",
    "--verify",
]
GPG_VERIFY_WRONG_KEYCHAIN_ARGS = GPG_COMMON_WRONG_KEYCHAIN_ARGS + [
    "--with-colons",
    "--verify",
]
TEST_VERIFY_FILE = os.path.join(CURRENT_TEST_DIR, "test_verify_file")


class TestGpGVerifyFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the temporary test files to sign
        if not exists(CURRENT_TEST_DIR):
            assert makedirs(CURRENT_TEST_DIR) is True
        # Gen sign test key
        assert (
            gen_key(
                TEST_KEY_NAME,
                key_generator=SignatureTypes.GPG,
                key_args=GPG_GEN_KEY_ARGS,
            )
            is True
        )
        cls.key_fingerprint = get_key_fingerprint(
            TEST_KEY_NAME,
            key_generator=SignatureTypes.GPG,
            key_args=GPG_GET_FINTERPRINT_ARGS,
        )
        assert cls.key_fingerprint is not None
        assert write(TEST_VERIFY_FILE, TEST_CONTENT) is True

    @classmethod
    def tearDownClass(cls):
        # Delete the class test key
        assert (
            delete_key(
                cls.key_fingerprint,
                delete_command=SignatureTypes.GPG,
                delete_args=GPG_DELETE_ARGS,
            )
            is True
        )
        # Remove the temporary directory and its contents
        assert remove(CURRENT_TEST_DIR, recursive=True) is True
        assert exists(CURRENT_TEST_DIR) is False

    def test_verify_failure(self):
        # Verify a file that has not been signed
        self.assertFalse(
            verify_file(
                TEST_VERIFY_FILE,
                TEST_KEY_NAME,
                verify_command=SignatureTypes.GPG,
                verify_args=GPG_VERIFY_ARGS,
            )
        )

    def test_sign_with_nonexisting_key(self):
        non_existing_key = "non_existing_key"
        # Sign the file with a non-existing key
        output_signed_file = (
            f"{TEST_VERIFY_FILE}-{non_existing_key}.{SignatureTypes.GPG}"
        )
        self.assertFalse(
            sign_file(
                TEST_VERIFY_FILE,
                non_existing_key,
                sign_command=SignatureTypes.GPG,
                sign_args=GPG_SIGN_ARGS,
                output=output_signed_file,
            )
        )
        self.assertFalse(exists(output_signed_file))

    def test_verify_success(self):
        # Sign the file to verify
        output_signed_file = f"{TEST_VERIFY_FILE}.{SignatureTypes.GPG}"
        self.assertTrue(
            sign_file(
                TEST_VERIFY_FILE,
                TEST_KEY_NAME,
                sign_command=SignatureTypes.GPG,
                sign_args=GPG_SIGN_ARGS,
                output=output_signed_file,
            )
        )
        self.assertTrue(
            verify_file(
                output_signed_file,
                TEST_KEY_NAME,
                verify_command=SignatureTypes.GPG,
                verify_args=GPG_VERIFY_ARGS,
            )
        )
        self.assertTrue(remove(output_signed_file))

    def test_verify_failure_wrong_keychain(self):
        # Sign the file to verify
        wrong_keychain = "wrong_keychain"
        output_signed_file = f"{TEST_VERIFY_FILE}-{wrong_keychain}.{SignatureTypes.GPG}"
        self.assertTrue(
            sign_file(
                TEST_VERIFY_FILE,
                TEST_KEY_NAME,
                sign_command=SignatureTypes.GPG,
                sign_args=GPG_SIGN_ARGS,
                output=output_signed_file,
            )
        )
        # Verify the signed file with a different key
        self.assertFalse(
            verify_file(
                output_signed_file,
                TEST_KEY_NAME,
                verify_command=SignatureTypes.GPG,
                verify_args=GPG_VERIFY_WRONG_KEYCHAIN_ARGS,
            )
        )
        self.assertTrue(remove(output_signed_file))

    def test_verify_additional_files_with_detach_signature(self):
        # Sign the file and output a detached signature
        output_signed_file = f"{TEST_VERIFY_FILE}-1.{SignatureTypes.GPG}"
        self.assertTrue(
            sign_file(
                TEST_VERIFY_FILE,
                TEST_KEY_NAME,
                sign_command=SignatureTypes.GPG,
                sign_args=GPG_DETACH_SIGN_ARGS,
                output=output_signed_file,
            )
        )
        self.assertTrue(exists(TEST_VERIFY_FILE))
        self.assertTrue(exists(output_signed_file))
        # Verify the signed file with additional files
        self.assertTrue(
            verify_file(
                output_signed_file,
                TEST_KEY_NAME,
                verify_command=SignatureTypes.GPG,
                verify_args=GPG_VERIFY_ARGS,
                verify_additional_files=[TEST_VERIFY_FILE],
            )
        )
        self.assertTrue(remove(output_signed_file))

    def test_verify_without_additional_detach_signature(self):
        # Sign the file and output a detached signature
        output_signed_file = f"{TEST_VERIFY_FILE}-2.{SignatureTypes.GPG}"
        self.assertTrue(
            sign_file(
                TEST_VERIFY_FILE,
                TEST_KEY_NAME,
                sign_command=SignatureTypes.GPG,
                sign_args=GPG_DETACH_SIGN_ARGS,
                output=output_signed_file,
            )
        )
        self.assertTrue(exists(TEST_VERIFY_FILE))
        self.assertTrue(exists(output_signed_file))
        # Verify should fail when missing the additional files for the detached signature
        self.assertFalse(
            verify_file(
                output_signed_file,
                TEST_KEY_NAME,
                verify_command=SignatureTypes.GPG,
                verify_args=GPG_VERIFY_ARGS,
            )
        )
        self.assertTrue(remove(output_signed_file))
