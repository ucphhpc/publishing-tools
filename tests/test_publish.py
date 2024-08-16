import os
import unittest

from publish.signature import SignatureTypes, gen_key
from publish.utils.io import makedirs, exists, remove, write, hashsum
from publish.publish import publish, PublishTypes, ChecksumTypes
from tests.common import TMP_TEST_PATH

TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)
TEST_PUBLISH_FILE = f"{TEST_NAME}_file"
TEST_PUBLISH_DESTINATION = f"{TEST_NAME}_destination"
TEST_FILE_CONTENT = "sfopawmdioamwioac aoimaw aw 2414 14"
TEST_FILE_CHECKSUM = "16f8f5519fcb700a5b8ceb3e5eeace66f04c003f2c898237c202403e724214f8"
CHECKSUM_ALGORITHM = ChecksumTypes.SHA256

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
GPG_SIGN_ARGS = GPG_SIGN_COMMON_ARGS + ["--sign", "--passphrase", ""]


class TestPublishFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a temporary directory to store the temporary test files to publish
        if not exists(CURRENT_TEST_DIR):
            assert makedirs(CURRENT_TEST_DIR) is True
        cls.publish_source = os.path.join(CURRENT_TEST_DIR, TEST_PUBLISH_FILE)
        assert write(cls.publish_source, TEST_FILE_CONTENT)
        assert exists(cls.publish_source)
        cls.publish_directory = os.path.join(CURRENT_TEST_DIR, TEST_PUBLISH_DESTINATION)
        if not exists(cls.publish_directory):
            assert makedirs(cls.publish_directory) is True

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory and its contents
        assert remove(CURRENT_TEST_DIR, recursive=True) is True
        assert not exists(CURRENT_TEST_DIR)

    def test_publish_file(self):
        publish_destination = os.path.join(
            self.publish_directory, f"{TEST_PUBLISH_FILE}-1"
        )
        self.assertTrue(
            publish(self.publish_source, publish_destination, PublishTypes.FILE)
        )
        self.assertTrue(exists(publish_destination))

    def test_source_file_checksum(self):
        # Get the checksum of the file
        checksum = hashsum(self.publish_source, algorithm=CHECKSUM_ALGORITHM)
        self.assertIsNotNone(checksum)
        self.assertEqual(checksum, TEST_FILE_CHECKSUM)

    def test_publish_file_with_checksum(self):
        # Publish the file with checksum
        publish_destination = os.path.join(
            self.publish_directory, f"{TEST_PUBLISH_FILE}-2"
        )
        self.assertTrue(
            publish(
                self.publish_source,
                publish_destination,
                PublishTypes.FILE,
                with_checksum=True,
                checksum_algorithm=CHECKSUM_ALGORITHM,
            )
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_destination + f".{CHECKSUM_ALGORITHM}"))

    def test_publish_file_with_signature(self):
        # Setup the key to sign the file with
        signature_key = f"{TEST_KEY_NAME}_1"
        self.assertTrue(
            gen_key(
                signature_key,
                key_generator=SignatureTypes.GPG,
                key_args=GPG_GEN_KEY_ARGS,
            )
        )

        # Publish the file with signature
        publish_destination = os.path.join(
            self.publish_directory, f"{TEST_PUBLISH_FILE}-3"
        )
        self.assertTrue(
            publish(
                self.publish_source,
                publish_destination,
                PublishTypes.FILE,
                with_signature=True,
                signature_generator=SignatureTypes.GPG,
                signature_key=signature_key,
                signauture_args=GPG_SIGN_ARGS,
            )
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_destination + f".{SignatureTypes.GPG}"))

    def test_publish_file_with_checksum_and_signature(self):
        # Setup the key to sign the file with
        signature_key = f"{TEST_KEY_NAME}_2"
        self.assertTrue(
            gen_key(
                signature_key,
                key_generator=SignatureTypes.GPG,
                key_args=GPG_GEN_KEY_ARGS,
            )
        )

        # Publish the file with checksum and signature
        publish_destination = os.path.join(
            self.publish_directory, f"{TEST_PUBLISH_FILE}-4"
        )
        self.assertTrue(
            publish(
                self.publish_source,
                publish_destination,
                PublishTypes.FILE,
                with_checksum=True,
                checksum_algorithm=CHECKSUM_ALGORITHM,
                with_signature=True,
                signature_generator=SignatureTypes.GPG,
                signature_key=signature_key,
                signauture_args=GPG_SIGN_ARGS,
            )
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_destination + f".{SignatureTypes.GPG}"))
        self.assertTrue(exists(publish_destination + f".{CHECKSUM_ALGORITHM}"))
