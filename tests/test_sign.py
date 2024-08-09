import os
import unittest

from publish.gpg import sign_file, gen_key, delete_key, get_key_fingerprint
from publish.utils.io import makedirs, exists, remove, write
import tests.base
from tests.common import (
    KEY_GENERATOR,
    GPG_GEN_KEY_ARGS,
    GPG_GET_FINGERPRINT_ARGS,
    GPG_SIGN_ARGS,
    GPG_DELETE_ARGS,
)


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_DIR = os.path.join(CURRENT_DIR, "tmp", "test_sign")

TEST_SIGN_FILE = "test_sign_file"
TEST_FILE_CONTENT = "sfopawmdioamwioac aoimaw aw 2414 14"

# GPG settings
TEST_KEY_NAME = "test_key"


class TestGpGSignFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the temporary test files to sign
        if not exists(TMP_TEST_DIR):
            assert makedirs(TMP_TEST_DIR) is True
        # Gen sign test key
        assert (
            gen_key(
                TEST_KEY_NAME, key_generator=KEY_GENERATOR, key_args=GPG_GEN_KEY_ARGS
            )
            is True
        )
        cls.key_fingerprint = get_key_fingerprint(
            TEST_KEY_NAME,
            key_generator=KEY_GENERATOR,
            key_args=GPG_GET_FINGERPRINT_ARGS,
        )
        assert cls.key_fingerprint is not None

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
        assert not exists(TMP_TEST_DIR)

    def test_generate_and_delete_sign_key(self):
        another_test_key = "another_test_key"
        self.assertTrue(
            gen_key(
                another_test_key, key_args=GPG_GEN_KEY_ARGS, key_generator=KEY_GENERATOR
            )
        )
        key_fingerprint = get_key_fingerprint(
            another_test_key,
            key_generator=KEY_GENERATOR,
            key_args=GPG_GET_FINGERPRINT_ARGS,
        )
        self.assertIsNotNone(key_fingerprint)
        self.assertTrue(
            delete_key(
                key_fingerprint,
                delete_command=KEY_GENERATOR,
                delete_args=GPG_DELETE_ARGS,
            )
        )

    def test_sign_success(self):
        # Create a temporary file to sign
        test_file_path = os.path.join(TMP_TEST_DIR, TEST_SIGN_FILE)
        self.assertTrue(write(test_file_path, TEST_FILE_CONTENT))
        self.assertTrue(exists(test_file_path))

        test_signed_file_ouput = f"{test_file_path}.{KEY_GENERATOR}"
        # Sign the temporary file
        self.assertTrue(
            sign_file(
                test_file_path,
                TEST_KEY_NAME,
                sign_command=KEY_GENERATOR,
                sign_args=GPG_SIGN_ARGS,
                output=test_signed_file_ouput,
            )
        )

        # Verify the signed file exists
        self.assertTrue(exists(test_signed_file_ouput))

    def test_sign_nonexisting_file_failure(self):
        # Sign a non-existent file
        non_existing_file = os.path.join(TMP_TEST_DIR, "non_existent_file")
        self.assertFalse(exists(non_existing_file))
        self.assertFalse(
            sign_file(
                non_existing_file,
                TEST_KEY_NAME,
                sign_command=KEY_GENERATOR,
                sign_args=GPG_SIGN_ARGS,
            )
        )
