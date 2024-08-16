import os
import unittest

from publish.utils.io import exists, makedirs, remove, hashsum, load
from publish.signature import gen_key, SignatureTypes
from publish.publish import publish, PublishTypes, ChecksumTypes
from publish.publish_container import build_image, remove_image
from tests.common import (
    TMP_TEST_PATH,
    TESTS_RESOURCES_DIR,
    TESTS_DOCKERFILE,
    LOCAL_OWNER,
    LOCAL_REGISTRY,
)


TEST_NAME = os.path.basename(__file__).split(".")[0]
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)

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

# Local image settings
TEST_PUBLISH_CONTAINER_IMAGE = f"{TEST_NAME}_container_image"
LOCAL_IMAGE_NAME = f"{LOCAL_REGISTRY}/{LOCAL_OWNER}/{TEST_PUBLISH_CONTAINER_IMAGE}"

# Archive settings
ARCHIVE_EXTENSION = "tar"
ARCHIVE_OUTPUT_PATH = os.path.join(
    CURRENT_TEST_DIR, f"{TEST_NAME}_archive.{ARCHIVE_EXTENSION}"
)

# Upload registry settings
DESTINATION_REGISTRY = "docker.io"
TEST_PUBLISH_DESTINATION = f"{DESTINATION_REGISTRY}://{TEST_PUBLISH_CONTAINER_IMAGE}"


class TestPublishContainerImage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not exists(CURRENT_TEST_DIR):
            assert makedirs(CURRENT_TEST_DIR) is True
        cls.publish_directory = os.path.join(CURRENT_TEST_DIR, TEST_PUBLISH_DESTINATION)
        if not exists(cls.publish_directory):
            assert makedirs(cls.publish_directory) is True
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

    def test_publish_image_to_archive(self):
        publish_destination = os.path.join(
            self.publish_directory,
            f"{TEST_PUBLISH_CONTAINER_IMAGE}.{ARCHIVE_EXTENSION}-1",
        )
        self.assertTrue(
            publish(
                LOCAL_IMAGE_NAME,
                publish_destination,
                PublishTypes.CONTAINER_IMAGE_ARCHIVE,
            )
        )
        self.assertTrue(exists(publish_destination))

    def test_publish_image_to_archive_with_checksum(self):
        publish_destination = os.path.join(
            self.publish_directory,
            f"{TEST_PUBLISH_CONTAINER_IMAGE}.{ARCHIVE_EXTENSION}-2",
        )
        publish_checksum_destination = f"{publish_destination}.{ChecksumTypes.SHA256}"
        self.assertTrue(
            publish(
                LOCAL_IMAGE_NAME,
                publish_destination,
                PublishTypes.CONTAINER_IMAGE_ARCHIVE,
                with_checksum=True,
                checksum_algorithm=ChecksumTypes.SHA256,
            )
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_checksum_destination))
        self.assertEqual(
            hashsum(publish_destination, algorithm=ChecksumTypes.SHA256),
            load(publish_checksum_destination),
        )

    def test_publish_image_to_archive_with_signature(self):
        # Setup the key to sign the file with
        signature_key = f"{TEST_KEY_NAME}_1"
        self.assertTrue(
            gen_key(
                signature_key,
                key_generator=SignatureTypes.GPG,
                key_args=GPG_GEN_KEY_ARGS,
            )
        )

        publish_destination = os.path.join(
            self.publish_directory,
            f"{TEST_PUBLISH_CONTAINER_IMAGE}.{ARCHIVE_EXTENSION}-2",
        )
        publish_signature_destination = f"{publish_destination}.{SignatureTypes.GPG}"
        # Sign the file with the key
        self.assertTrue(
            publish(
                LOCAL_IMAGE_NAME,
                publish_destination,
                PublishTypes.CONTAINER_IMAGE_ARCHIVE,
                with_signature=True,
                signature_generator=SignatureTypes.GPG,
                signature_key=signature_key,
                signauture_args=GPG_SIGN_ARGS,
            )
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_signature_destination))
