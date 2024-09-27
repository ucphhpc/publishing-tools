import os
import unittest

from publish.signature import (
    gen_key,
    delete_key,
    get_key_fingerprint,
    SignatureTypes,
)
from publish.utils.io import exists, makedirs, remove, write
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, SIGN_FAILURE
from publish.cli.sign import main
from tests.common import (
    TMP_TEST_PATH,
    TEST_CONTENT,
    TEST_FILE,
    NON_EXISTING_FILE,
    NON_EXISTING_KEY,
)

TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)
TEST_KEY_NAME = f"{TEST_NAME}_key"

TMP_TEST_GNUPG_DIR = os.path.join(CURRENT_TEST_DIR, ".gnupg")
GPG_TEST_SIGN_KEYRING = f"{TEST_NAME}.{SignatureTypes.GPG}"
GPG_SIGN_COMMON_ARGS = [
    "--homedir",
    TMP_TEST_GNUPG_DIR,
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


class TestSignCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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

    def test_help_msg(self):
        return_code = None
        try:
            _ = main(["-h"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_file_not_found(self):
        self.assertEqual(main([NON_EXISTING_FILE, NON_EXISTING_KEY]), FILE_NOT_FOUND)

    def test_sign_failure(self):
        test_sign_file = os.path.join(CURRENT_TEST_DIR, f"{TEST_FILE}-1")
        self.assertTrue(write(test_sign_file, TEST_CONTENT))
        self.assertTrue(exists(test_sign_file))

        test_sign_file_output = f"{test_sign_file}.{SignatureTypes.GPG}"
        self.assertEqual(
            main(
                [
                    test_sign_file,
                    NON_EXISTING_KEY,
                    "--signature-args",
                    GPG_SIGN_ARGS,
                    "--output",
                    test_sign_file_output,
                ]
            ),
            SIGN_FAILURE,
        )

    def test_sign_success(self):
        test_sign_file = os.path.join(CURRENT_TEST_DIR, f"{TEST_FILE}-2")
        self.assertTrue(write(test_sign_file, TEST_CONTENT))
        self.assertTrue(exists(test_sign_file))

        test_sign_file_output = f"{test_sign_file}.{SignatureTypes.GPG}"
        self.assertEqual(
            main(
                [
                    test_sign_file,
                    TEST_KEY_NAME,
                    "--signature-args",
                    GPG_SIGN_ARGS,
                    "--output",
                    test_sign_file_output,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(f"{test_sign_file}.{SignatureTypes.GPG}"))

    def test_sign_remove_original(self):
        test_sign_file = os.path.join(CURRENT_TEST_DIR, f"{TEST_FILE}-3")
        self.assertTrue(write(test_sign_file, TEST_CONTENT))
        self.assertTrue(exists(test_sign_file))

        test_sign_file_output = f"{test_sign_file}.{SignatureTypes.GPG}"
        self.assertEqual(
            main(
                [
                    test_sign_file,
                    TEST_KEY_NAME,
                    "--signature-args",
                    GPG_SIGN_ARGS,
                    "--output",
                    test_sign_file_output,
                    "--remove-original",
                ]
            ),
            SUCCESS,
        )
        self.assertFalse(exists(test_sign_file))
        self.assertTrue(exists(test_sign_file_output))

    def test_sign_detach_signature(self):
        test_sign_file = os.path.join(CURRENT_TEST_DIR, f"{TEST_FILE}-4")
        self.assertTrue(write(test_sign_file, TEST_CONTENT))
        self.assertTrue(exists(test_sign_file))

        test_sign_file_output = f"{test_sign_file}.{SignatureTypes.GPG}"
        self.assertEqual(
            main(
                [
                    test_sign_file,
                    TEST_KEY_NAME,
                    "--signature-args",
                    GPG_DETACH_SIGN_ARGS,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(test_sign_file))
        self.assertTrue(exists(test_sign_file_output))
