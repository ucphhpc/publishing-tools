import os
import unittest

from publish.signature import (
    sign_file,
    gen_key,
    delete_key,
    get_key_fingerprint,
    SignatureTypes,
)
from publish.utils.io import makedirs, exists, remove, write
from tests.common import TMP_TEST_PATH, TEST_FILE, TEST_CONTENT, NON_EXISTING_FILE

TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)

# GPG settings
TEST_KEY_NAME = f"{TEST_NAME}_key"
TMP_TEST_GNUPG_DIR = os.path.join(CURRENT_TEST_DIR, ".gnupg")
GPG_TEST_SIGN_KEYRING = f"{TEST_KEY_NAME}.{SignatureTypes.GPG}"
GPG_SIGN_COMMON_ARGS = [
    "--homedir",
    CURRENT_TEST_DIR,
    "--no-default-keyring",
    "--keyring",
    GPG_TEST_SIGN_KEYRING,
    "--no-tty",
    "--batch",
]
GPG_GEN_KEY_ARGS = GPG_SIGN_COMMON_ARGS + [
    "--quick-gen-key",
    "--passphrase",
    "",
]
GPG_GET_FINGERPRINT_ARGS = GPG_SIGN_COMMON_ARGS + [
    "--with-colons",
    "--fingerprint",
]
GPG_SIGN_ARGS = GPG_SIGN_COMMON_ARGS + ["--sign", "--passphrase", ""]
GPG_DETACH_SIGN_ARGS = GPG_SIGN_COMMON_ARGS + ["--detach-sign", "--passphrase", ""]
GPG_DELETE_ARGS = GPG_SIGN_COMMON_ARGS + [
    "--delete-secret-and-public-key",
    "--yes",
]


class TestGpGSignFile(unittest.TestCase):
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
            key_args=GPG_GET_FINGERPRINT_ARGS,
        )
        assert cls.key_fingerprint is not None

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
        assert not exists(CURRENT_TEST_DIR)

    def test_generate_and_delete_sign_key(self):
        another_test_key = "another_test_key"
        self.assertTrue(
            gen_key(
                another_test_key,
                key_args=GPG_GEN_KEY_ARGS,
                key_generator=SignatureTypes.GPG,
            )
        )
        key_fingerprint = get_key_fingerprint(
            another_test_key,
            key_generator=SignatureTypes.GPG,
            key_args=GPG_GET_FINGERPRINT_ARGS,
        )
        self.assertIsNotNone(key_fingerprint)
        self.assertTrue(
            delete_key(
                key_fingerprint,
                delete_command=SignatureTypes.GPG,
                delete_args=GPG_DELETE_ARGS,
            )
        )

    def test_sign_success(self):
        # Create a temporary file to sign
        test_file_path = os.path.join(CURRENT_TEST_DIR, f"{TEST_FILE}-1")
        self.assertTrue(write(test_file_path, TEST_CONTENT))
        self.assertTrue(exists(test_file_path))

        test_signed_file_ouput = f"{test_file_path}.{SignatureTypes.GPG}"
        # Sign the temporary file
        self.assertTrue(
            sign_file(
                test_file_path,
                TEST_KEY_NAME,
                sign_command=SignatureTypes.GPG,
                sign_args=GPG_SIGN_ARGS,
                output=test_signed_file_ouput,
            )
        )

        # Verify the signed file exists
        self.assertTrue(exists(test_signed_file_ouput))

    def test_sign_nonexisting_file_failure(self):
        # Sign a non-existent file
        non_existing_file = os.path.join(CURRENT_TEST_DIR, NON_EXISTING_FILE)
        self.assertFalse(exists(non_existing_file))
        self.assertFalse(
            sign_file(
                non_existing_file,
                TEST_KEY_NAME,
                sign_command=SignatureTypes.GPG,
                sign_args=GPG_SIGN_ARGS,
            )
        )

    def test_sign_detach_signature(self):
        # Create a temporary file to sign
        test_file_path = os.path.join(CURRENT_TEST_DIR, f"{TEST_FILE}-2")
        self.assertTrue(write(test_file_path, TEST_CONTENT))
        self.assertTrue(exists(test_file_path))

        test_detached_signed_file_ouput = f"{test_file_path}.{SignatureTypes.GPG}"
        # Sign the temporary file
        self.assertTrue(
            sign_file(
                test_file_path,
                TEST_KEY_NAME,
                sign_command=SignatureTypes.GPG,
                sign_args=GPG_DETACH_SIGN_ARGS,
            )
        )

        # Verify the signed file exists
        self.assertTrue(exists(test_file_path))
        self.assertTrue(exists(test_detached_signed_file_ouput))
