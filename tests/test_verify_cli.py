import os
import unittest

from publish.utils.io import exists, makedirs, remove, write
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, VERIFY_FAILURE
from publish.cli.verify import main
from tests.common import TMP_TEST_PATH


TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)
NON_EXISTING_FILE = "non_existing_file"
NON_EXISTING_KEY = "non_existing_key"


class TestVerifyCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not exists(CURRENT_TEST_DIR):
            assert makedirs(CURRENT_TEST_DIR) is True

    @classmethod
    def tearDownClass(cls):
        assert remove(CURRENT_TEST_DIR, recursive=True) is True
        assert not exists(CURRENT_TEST_DIR)

    def test_help_msg(self):
        return_code = None
        try:
            _ = main(["-h"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_file_not_found(self):
        file_ = NON_EXISTING_FILE
        key = NON_EXISTING_KEY
        self.assertEqual(main([file_, key]), FILE_NOT_FOUND)

    def test_verify_failure(self):
        test_sign_file = os.path.join(CURRENT_TEST_DIR, "test_sign_failure_file")
        test_sign_file_content = "foo bar"
        self.assertTrue(write(test_sign_file, test_sign_file_content))
        self.assertTrue(exists(test_sign_file))

        key = NON_EXISTING_KEY
        self.assertEqual(main([test_sign_file, key]), VERIFY_FAILURE)

        self.assertTrue(remove(test_sign_file))
        self.assertFalse(exists(test_sign_file))
