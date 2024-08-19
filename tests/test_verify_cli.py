import os
import unittest

from publish.utils.io import exists, makedirs, remove, write
from publish.signature import gen_key, SignatureTypes
from publish.checksum import write_checksum_file, ChecksumTypes
from publish.cli.return_codes import (
    SUCCESS,
    FILE_NOT_FOUND,
    VERIFY_FAILURE,
    CHECKSUM_FAILURE,
)
from publish.cli.verify import main
from tests.common import TMP_TEST_PATH, TEST_CONTENT


TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)
TEST_KEY_NAME = f"{TEST_NAME}_key"

NON_EXISTING_FILE = "non_existing_file"
NON_EXISTING_KEY = "non_existing_key"

# GPG settings
TMP_TEST_GNUPG_DIR = os.path.join(CURRENT_TEST_DIR, ".gnupg")
# Regular custom gpg keychain tests
GPG_VERIFY_KEYRING = f"{TEST_NAME}-keyring.{SignatureTypes.GPG}"
GPG_COMMON_ARGS = [
    "--homedir",
    TMP_TEST_GNUPG_DIR,
    "--no-default-keyring",
    "--keyring",
    GPG_VERIFY_KEYRING,
    "--no-tty",
    "--batch",
]
GPG_GEN_KEY_ARGS = GPG_COMMON_ARGS + [
    "--quick-gen-key",
    "--passphrase",
    "",
]
GPG_SIGN_ARGS = GPG_COMMON_ARGS + [
    "--sign",
    "--passphrase",
    "",
]
TEST_VERIFY_FILE = os.path.join(CURRENT_TEST_DIR, "test_verify_file")


class TestVerifyCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not exists(CURRENT_TEST_DIR):
            assert makedirs(CURRENT_TEST_DIR) is True
        assert (
            gen_key(
                TEST_KEY_NAME,
                key_generator=SignatureTypes.GPG,
                key_args=GPG_GEN_KEY_ARGS,
            )
            is True
        )
        assert write(TEST_VERIFY_FILE, TEST_CONTENT) is True

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
        test_verify_file = os.path.join(CURRENT_TEST_DIR, "{TEST_VERIFY_FILE}-1")
        self.assertTrue(write(test_verify_file, TEST_CONTENT))
        self.assertTrue(exists(test_verify_file))

        key = NON_EXISTING_KEY
        self.assertEqual(main([test_verify_file, key]), VERIFY_FAILURE)
        self.assertTrue(remove(test_verify_file))
        self.assertFalse(exists(test_verify_file))

    def test_verify_success(self):
        test_verify_file = os.path.join(CURRENT_TEST_DIR, f"{TEST_VERIFY_FILE}-2")
        self.assertTrue(write(test_verify_file, TEST_CONTENT))
        self.assertTrue(exists(test_verify_file))
        self.assertEqual(
            main([test_verify_file, TEST_KEY_NAME, "--verify-args", GPG_SIGN_ARGS]),
            SUCCESS,
        )

    def test_verify_success_with_checksum(self):
        test_verify_file = os.path.join(CURRENT_TEST_DIR, f"{TEST_VERIFY_FILE}-3")
        self.assertTrue(write(test_verify_file, TEST_CONTENT))
        self.assertTrue(exists(test_verify_file))
        self.assertTrue(
            write_checksum_file(test_verify_file, algorithm=ChecksumTypes.SHA256)
        )
        checksum_file = f"{test_verify_file}.{ChecksumTypes.SHA256}"
        self.assertTrue(exists(checksum_file))
        self.assertEqual(
            main(
                [
                    test_verify_file,
                    TEST_KEY_NAME,
                    "--verify-args",
                    GPG_SIGN_ARGS,
                    "--with-checksum",
                    "--checksum-file",
                    checksum_file,
                    "--checksum-algorithm",
                    ChecksumTypes.SHA256,
                ]
            ),
            SUCCESS,
        )

    def test_verify_checksum_failure(self):
        test_verify_file = os.path.join(CURRENT_TEST_DIR, f"{TEST_VERIFY_FILE}-4")
        self.assertTrue(write(test_verify_file, TEST_CONTENT))
        self.assertTrue(exists(test_verify_file))
        self.assertTrue(
            write_checksum_file(test_verify_file, algorithm=ChecksumTypes.MD5)
        )
        checksum_file = f"{test_verify_file}.{ChecksumTypes.MD5}"
        self.assertEqual(
            main(
                [
                    test_verify_file,
                    TEST_KEY_NAME,
                    "--verify-args",
                    GPG_SIGN_ARGS,
                    "--with-checksum",
                    "--checksum-file",
                    checksum_file,
                    "--checksum-algorithm",
                    ChecksumTypes.SHA256,
                ]
            ),
            CHECKSUM_FAILURE,
        )
        self.assertTrue(remove(test_verify_file))
        self.assertFalse(exists(test_verify_file))
        self.assertTrue(remove(checksum_file))
        self.assertFalse(exists(checksum_file))
