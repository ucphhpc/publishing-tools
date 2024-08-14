import os
import unittest

from publish.gpg import gen_key, delete_key, get_key_fingerprint
from publish.utils.io import exists, makedirs, remove, write
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, SIGN_FAILURE
from publish.cli.sign import main
import tests.base
from tests.common import TMP_TEST_PATH, KEY_GENERATOR

TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)
TEST_KEY_NAME = f"{TEST_NAME}_key"

TMP_TEST_GNUPG_DIR = os.path.join(CURRENT_TEST_DIR, ".gnupg")
GPG_TEST_SIGN_KEYRING = f"{TEST_NAME}.gpg"
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


class TestSignCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not exists(CURRENT_TEST_DIR):
            assert makedirs(CURRENT_TEST_DIR) is True
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
        key = "non_existing_key"
        file_ = "non_existing_file"
        return_code = main([file_, key])
        self.assertEqual(return_code, FILE_NOT_FOUND)

    def test_sign_failure(self):
        test_sign_file = os.path.join(CURRENT_TEST_DIR, "test_sign_failure_file")
        test_sign_file_content = "foo bar"
        self.assertTrue(write(test_sign_file, test_sign_file_content))
        self.assertTrue(exists(test_sign_file))

        test_sign_file_output = f"{test_sign_file}.{KEY_GENERATOR}"
        key = "non_existing_key"
        self.assertEqual(
            main(
                [
                    test_sign_file,
                    key,
                    "--sign-args",
                    GPG_SIGN_ARGS,
                    "--output",
                    test_sign_file_output,
                ]
            ),
            SIGN_FAILURE,
        )

    def test_sign_success(self):
        test_sign_file = os.path.join(CURRENT_TEST_DIR, "test_sign_success_file")
        test_sign_file_content = "adm0ad9am d0a9m2doim"
        self.assertTrue(write(test_sign_file, test_sign_file_content))
        self.assertTrue(exists(test_sign_file))

        test_sign_file_output = f"{test_sign_file}.{KEY_GENERATOR}"
        self.assertEqual(
            main(
                [
                    test_sign_file,
                    TEST_KEY_NAME,
                    "--sign-args",
                    GPG_SIGN_ARGS,
                    "--output",
                    test_sign_file_output,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(f"{test_sign_file}.{KEY_GENERATOR}"))
