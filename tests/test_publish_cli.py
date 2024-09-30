import unittest
import os

from publish.utils.io import exists, makedirs, remove, write, load, hashsum
from publish.signature import gen_key, SignatureTypes, SignatureSources
from publish.publish_container import build_image, remove_image
from publish.cli.return_codes import SUCCESS, FILE_NOT_FOUND, IMAGE_NOT_FOUND
from publish.cli.publish import main, ChecksumTypes, PublishTypes
from tests.common import (
    TMP_TEST_PATH,
    TESTS_RESOURCES_DIR,
    TESTS_DOCKERFILE,
    LOCAL_OWNER,
    LOCAL_REGISTRY,
    NON_EXISTING_FILE,
    NON_EXISTING_IMAGE,
    NON_EXISTING_DESTINATION,
    ARCHIVE_EXTENSION,
    TEST_CONTENT,
)

TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)

# Publish settings
TEST_PUBLISH_FILE = f"{TEST_NAME}_file"
TEST_PUBLISH_DESTINATION = f"{TEST_NAME}_destination"
TEST_PUBLISH_DIRECTORY = os.path.join(CURRENT_TEST_DIR, TEST_PUBLISH_DESTINATION)
TEST_PUBLISH_INPUT = os.path.join(TEST_PUBLISH_DIRECTORY, TEST_PUBLISH_FILE)

# Publish image settings
TEST_PUBLISH_CONTAINER_IMAGE = f"{TEST_NAME}_container_image"
LOCAL_IMAGE_NAME = f"{LOCAL_REGISTRY}/{LOCAL_OWNER}/{TEST_PUBLISH_CONTAINER_IMAGE}"

PUBLISH_TYPE_SOURCE = {
    PublishTypes.FILE: TEST_PUBLISH_INPUT,
    PublishTypes.CONTAINER_IMAGE_ARCHIVE: LOCAL_IMAGE_NAME,
}

PUBLISH_TYPE_EXTENSION = {
    PublishTypes.FILE: "",
    PublishTypes.CONTAINER_IMAGE_ARCHIVE: f".{ARCHIVE_EXTENSION}",
}

# GPG Settings
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
GPG_DETACH_SIGN_ARGS = GPG_SIGN_COMMON_ARGS + ["--detach-sign", "--passphrase", ""]


class TestPublishCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not exists(CURRENT_TEST_DIR):
            assert makedirs(CURRENT_TEST_DIR) is True
        if not exists(TEST_PUBLISH_DIRECTORY):
            assert makedirs(TEST_PUBLISH_DIRECTORY) is True
        assert write(TEST_PUBLISH_INPUT, TEST_CONTENT)
        assert exists(TEST_PUBLISH_INPUT)
        assert (
            build_image(
                path=TESTS_RESOURCES_DIR,
                dockerfile=TESTS_DOCKERFILE,
                tag=LOCAL_IMAGE_NAME,
            )
            is True
        )

    @classmethod
    def tearDownClass(cls):
        assert remove(CURRENT_TEST_DIR, recursive=True) is True
        assert not exists(CURRENT_TEST_DIR)
        assert remove_image(LOCAL_IMAGE_NAME) is True

    def test_help_msg(self):
        return_code = None
        try:
            _ = main(["-h"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_publish_file_not_found(self):
        self.assertEqual(
            main([NON_EXISTING_FILE, NON_EXISTING_DESTINATION]), FILE_NOT_FOUND
        )

    def test_publish_file_success(self):
        publish_destination = (
            f"{TEST_PUBLISH_INPUT}{PUBLISH_TYPE_EXTENSION[PublishTypes.FILE]}-1"
        )
        self.assertEqual(
            main(
                [
                    PUBLISH_TYPE_SOURCE[PublishTypes.FILE],
                    publish_destination,
                    "--publish-type",
                    PublishTypes.FILE,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(publish_destination))

    def test_publish_image_not_found(self):
        self.assertEqual(
            main(
                [
                    NON_EXISTING_IMAGE,
                    NON_EXISTING_DESTINATION,
                    "--publish-type",
                    PublishTypes.CONTAINER_IMAGE_ARCHIVE,
                ]
            ),
            IMAGE_NOT_FOUND,
        )

    def test_publish_success_image(self):
        publish_destination = f"{TEST_PUBLISH_INPUT}{PUBLISH_TYPE_EXTENSION[PublishTypes.CONTAINER_IMAGE_ARCHIVE]}-1"
        self.assertEqual(
            main(
                [
                    PUBLISH_TYPE_SOURCE[PublishTypes.CONTAINER_IMAGE_ARCHIVE],
                    publish_destination,
                    "--publish-type",
                    PublishTypes.CONTAINER_IMAGE_ARCHIVE,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(publish_destination))

    def test_publish_file_with_checksum(self):
        publish_destination = (
            f"{TEST_PUBLISH_INPUT}{PUBLISH_TYPE_EXTENSION[PublishTypes.FILE]}-1"
        )
        for checksum_type in ChecksumTypes:
            publish_checksum_destination = (
                f"{publish_destination}.{checksum_type.value}"
            )
            self.assertEqual(
                main(
                    [
                        PUBLISH_TYPE_SOURCE[PublishTypes.FILE],
                        publish_destination,
                        "--publish-type",
                        PublishTypes.FILE,
                        "--with-checksum",
                        "--checksum-algorithm",
                        checksum_type.value,
                    ]
                ),
                SUCCESS,
            )
            self.assertTrue(exists(publish_destination))
            self.assertTrue(exists(publish_checksum_destination))
            self.assertEqual(
                hashsum(publish_destination, algorithm=checksum_type.value),
                load(publish_checksum_destination),
            )

    def test_publish_image_with_checksum(self):
        publish_destination = f"{TEST_PUBLISH_INPUT}{PUBLISH_TYPE_EXTENSION[PublishTypes.CONTAINER_IMAGE_ARCHIVE]}-1"
        for checksum_type in ChecksumTypes:
            publish_checksum_destination = (
                f"{publish_destination}.{checksum_type.value}"
            )
            self.assertEqual(
                main(
                    [
                        PUBLISH_TYPE_SOURCE[PublishTypes.CONTAINER_IMAGE_ARCHIVE],
                        publish_destination,
                        "--publish-type",
                        PublishTypes.CONTAINER_IMAGE_ARCHIVE,
                        "--with-checksum",
                        "--checksum-algorithm",
                        checksum_type.value,
                    ]
                ),
                SUCCESS,
            )
            self.assertTrue(exists(publish_destination))
            self.assertTrue(exists(publish_checksum_destination))
            self.assertEqual(
                hashsum(publish_destination, algorithm=checksum_type.value),
                load(publish_checksum_destination),
            )

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

        publish_destination = (
            f"{TEST_PUBLISH_INPUT}{PUBLISH_TYPE_EXTENSION[PublishTypes.FILE]}-3"
        )
        publish_signature_destination = f"{publish_destination}.{SignatureTypes.GPG}"
        self.assertEqual(
            main(
                [
                    PUBLISH_TYPE_SOURCE[PublishTypes.FILE],
                    publish_destination,
                    "--publish-type",
                    PublishTypes.FILE,
                    "--with-signature",
                    "--signature-generator",
                    SignatureTypes.GPG,
                    "--signature-key",
                    signature_key,
                    "--signature-args",
                    GPG_SIGN_ARGS,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_signature_destination))

    def test_publish_with_detached_signature(self):
        # Setup the key to sign the file with
        signature_key = f"{TEST_KEY_NAME}_2"
        self.assertTrue(
            gen_key(
                signature_key,
                key_generator=SignatureTypes.GPG,
                key_args=GPG_GEN_KEY_ARGS,
            )
        )

        # Publish the file with detached signature
        publish_destination = (
            f"{TEST_PUBLISH_INPUT}{PUBLISH_TYPE_EXTENSION[PublishTypes.FILE]}-4"
        )
        publish_signature_destination = f"{publish_destination}.{SignatureTypes.GPG}"
        self.assertEqual(
            main(
                [
                    PUBLISH_TYPE_SOURCE[PublishTypes.FILE],
                    publish_destination,
                    "--publish-type",
                    PublishTypes.FILE,
                    "--with-signature",
                    "--signature-generator",
                    SignatureTypes.GPG,
                    "--signature-key",
                    signature_key,
                    "--signature-args",
                    GPG_DETACH_SIGN_ARGS,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_signature_destination))

    def test_publish_image_with_detached_signature(self):
        # Setup the key to sign the file with
        signature_key = f"{TEST_KEY_NAME}_3"
        self.assertTrue(
            gen_key(
                signature_key,
                key_generator=SignatureTypes.GPG,
                key_args=GPG_GEN_KEY_ARGS,
            )
        )

        publish_destination = f"{TEST_PUBLISH_INPUT}{PUBLISH_TYPE_EXTENSION[PublishTypes.CONTAINER_IMAGE_ARCHIVE]}-3"
        publish_signature_destination = f"{publish_destination}.{SignatureTypes.GPG}"
        self.assertEqual(
            main(
                [
                    PUBLISH_TYPE_SOURCE[PublishTypes.CONTAINER_IMAGE_ARCHIVE],
                    publish_destination,
                    "--publish-type",
                    PublishTypes.CONTAINER_IMAGE_ARCHIVE,
                    "--with-signature",
                    "--signature-generator",
                    SignatureTypes.GPG,
                    "--signature-key",
                    signature_key,
                    "--signature-args",
                    GPG_DETACH_SIGN_ARGS,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_signature_destination))

    def test_publish_with_signed_checksum(self):
        # Setup the key to sign the file with
        signature_key = f"{TEST_KEY_NAME}_4"
        self.assertTrue(
            gen_key(
                signature_key,
                key_generator=SignatureTypes.GPG,
                key_args=GPG_GEN_KEY_ARGS,
            )
        )

        # Publish the file with detached signature
        publish_destination = (
            f"{TEST_PUBLISH_INPUT}{PUBLISH_TYPE_EXTENSION[PublishTypes.FILE]}-5"
        )
        self.assertEqual(
            main(
                [
                    PUBLISH_TYPE_SOURCE[PublishTypes.FILE],
                    publish_destination,
                    "--publish-type",
                    PublishTypes.FILE,
                    "--with-checksum",
                    "--checksum-algorithm",
                    ChecksumTypes.SHA256.value,
                    "--with-signature",
                    "--signature-generator",
                    SignatureTypes.GPG,
                    "--signature-source",
                    SignatureSources.GENERATED_CHECKSUM_FILE,
                    "--signature-key",
                    signature_key,
                    "--signature-args",
                    GPG_SIGN_ARGS,
                ]
            ),
            SUCCESS,
        )
        self.assertTrue(exists(publish_destination))
        self.assertFalse(exists(f"{publish_destination}.{SignatureTypes.GPG}"))
        output_checksum_file = f"{publish_destination}.{ChecksumTypes.SHA256.value}"
        self.assertTrue(exists(output_checksum_file))
        self.assertTrue(exists(output_checksum_file + f".{SignatureTypes.GPG}"))
