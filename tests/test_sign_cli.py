import os
import unittest

import tests.base
from publish.utils.io import exists, makedirs, remove, write
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, SIGN_FAILURE
from publish.cli.sign import main
from tests.common import (
    KEY_GENERATOR,
    GPG_GEN_KEY_ARGS,
    GPG_GET_FINGERPRINT_ARGS,
    GPG_SIGN_ARGS,
    GPG_DELETE_ARGS,
)

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_DIR = os.path.join(CURRENT_DIR, "tmp", "test_sign_cli")
TEST_KEY_NAME = "test_sign_key"


class TestSignCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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

    def test_help_msg(self):
        return_code = None
        try:
            _ = main(["-h"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_file_not_found(self):
        key = "non_existing_key"
        file_ = "non_existing_file"
        return_code = main([file_, key])
        self.assertEqual(return_code, FILE_NOT_FOUND)

    def test_sign_failure(self):
        test_file_path = os.path.join(TMP_TEST_DIR, "test_sign_failure_file")
        test_sign_file_content = "foo bar"
        self.assertTrue(write(test_file_path, test_sign_file_content))
        self.assertTrue(exists(test_file_path))

        key = "non_existing_key"
        self.assertEqual(main([test_file_path, key]), SIGN_FAILURE)
        self.assertTrue(remove(test_file_path))
        self.assertFalse(exists(test_file_path))

    def test_sign_success(self):
        test_sign_file = "test_sign_success_file"
        test_sign_file_content = "adm0ad9am d0a9m2doim"
        self.assertTrue(write(test_sign_file, test_sign_file_content))
        self.assertTrue(exists(test_sign_file))

        self.assertEqual(main([test_sign_file, TEST_KEY_NAME]), SUCCESS)
        self.assertTrue(exists(f"{test_sign_file}.{KEY_GENERATOR}"))

        self.assertTrue(remove(test_sign_file))
        self.assertFalse(exists(test_sign_file))
