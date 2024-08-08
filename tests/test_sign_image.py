import os
import unittest

import tests.base
from publish.gpg import sign_file, gen_key, delete_key, get_key_fingerprint
from publish.utils.io import makedirs, exists, remove, write


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_DIR = os.path.join(CURRENT_DIR, "tmp", "test_sign")

KEY_GENERATOR = "gpg"
TEST_KEY_NAME = "test_key"
GPG_GEN_KEY_ARGS = ["--no-tty", "--batch", "--quick-gen-key", "--passphrase", ""]
GPG_SIGN_ARGS = ["--no-tty", "--batch", "--sign", "--passphrase", ""]


class TestGpGSignFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the temporary test files to sign
        if not exists(TMP_TEST_DIR):
            assert makedirs(TMP_TEST_DIR) is True
        # Gen sign test key
        assert (
            gen_key(
                TEST_KEY_NAME, key_args=GPG_GEN_KEY_ARGS, key_generator=KEY_GENERATOR
            )
            is True
        )
        cls.key_fingerprint = get_key_fingerprint(
            TEST_KEY_NAME, key_generator=KEY_GENERATOR
        )
        assert cls.key_fingerprint is not None

    @classmethod
    def tearDownClass(cls):
        # Delete the class test key
        assert delete_key(cls.key_fingerprint, key_generator=KEY_GENERATOR) is True
        # Remove the temporary directory and its contents
        assert remove(TMP_TEST_DIR, recursive=True) is True

    def test_generate_and_delete_sign_key(self):
        another_test_key = "another_test_key"
        self.assertTrue(
            gen_key(
                another_test_key, key_args=GPG_GEN_KEY_ARGS, key_generator=KEY_GENERATOR
            )
        )
        key_fingerprint = get_key_fingerprint(
            another_test_key, key_generator=KEY_GENERATOR
        )
        self.assertIsNotNone(key_fingerprint)
        self.assertTrue(delete_key(key_fingerprint, key_generator=KEY_GENERATOR))

    def test_sign_success(self):
        # Create a temporary file to sign
        test_file = os.path.join(TMP_TEST_DIR, "test_sign_file")
        self.assertTrue(write(test_file, "test content"))
        self.assertTrue(exists(test_file))

        # Sign the temporary file
        self.assertTrue(
            sign_file(
                test_file,
                TEST_KEY_NAME,
                sign_args=GPG_SIGN_ARGS,
                sign_command=KEY_GENERATOR,
                output=f"{test_file}.{KEY_GENERATOR}",
            )
        )

        # Verify the signed file exists
        signed_file = f"{test_file}.{KEY_GENERATOR}"
        self.assertTrue(exists(signed_file))

        # Cleanup the temporary files
        self.assertTrue(remove(signed_file))
        self.assertTrue(remove(test_file))

    def test_sign_nonexisting_file_failure(self):
        # Sign a non-existent file
        test_file = os.path.join(TMP_TEST_DIR, "non_existent_file")
        self.assertFalse(exists(test_file))
        self.assertFalse(
            sign_file(test_file, TEST_KEY_NAME, sign_command=KEY_GENERATOR)
        )
