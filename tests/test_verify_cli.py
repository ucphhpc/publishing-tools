import os
import unittest

import tests.base
from publish.utils.io import exists, makedirs, remove, write
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, VERIFY_FAILURE
from publish.cli.verify import main

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_DIR = os.path.join(CURRENT_DIR, "tmp", "test_verify_cli")


class TestVerifyCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not exists(TMP_TEST_DIR):
            assert makedirs(TMP_TEST_DIR) is True

    @classmethod
    def tearDownClass(cls):
        assert remove(TMP_TEST_DIR) is True
        assert not exists(TMP_TEST_DIR)

    def test_help_msg(self):
        return_code = None
        try:
            _ = main(["-h"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_file_not_found(self):
        file_ = "non_existing_file"
        key = "non_existing_key"
        self.assertEqual(main([file_, key]), FILE_NOT_FOUND)

    def test_verify_failure(self):
        test_sign_file = "test_sign_failure_file"
        test_sign_file_content = "foo bar"
        self.assertTrue(write(test_sign_file, test_sign_file_content))
        self.assertTrue(exists(test_sign_file))

        key = "non_existing_key"
        self.assertEqual(main([test_sign_file, key]), VERIFY_FAILURE)
