import os
import unittest

from publish.utils.io import exists, makedirs, remove, hashsum, load
from publish.signature import gen_key, SignatureTypes
from publish.publish import publish, PublishTypes, ChecksumTypes
from publish.publish_container import build_image, remove_image
from tests.common import TMP_TEST_PATH, BASE_TESTS_PATH


TEST_NAME = os.path.basename(__file__).split(".")[0]
TESTS_RESOURCES_DIR = os.path.join(BASE_TESTS_PATH, "res")
CURRENT_TEST_DIR = os.path.join(TMP_TEST_PATH, TEST_NAME)
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
GPG_GEN_KEY_ARGS = GPG_SIGN_COMMON_ARGS + ["--quick-gen-key", "--passphrase", ""]
GPG_SIGN_ARGS = GPG_SIGN_COMMON_ARGS + ["--sign", "--passphrase", ""]

# Local image settings
LOCAL_REGISTRY = "localhost"
LOCAL_OWNER = "test"
TEST_PUBLISH_CONTAINER_IMAGE = f"{TEST_NAME}_container_image"
LOCAL_IMAGE_DOCKERFILE = os.path.join(TESTS_RESOURCES_DIR, "Dockerfile")
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
        # Create a temporary directory to store the temporary test files to sign
        if not exists(CURRENT_TEST_DIR):
            assert makedirs(CURRENT_TEST_DIR) is True
        cls.publish_directory = os.path.join(CURRENT_TEST_DIR, TEST_PUBLISH_DESTINATION)
        if not exists(cls.publish_directory):
            assert makedirs(cls.publish_directory) is True
        # TODO: Build the container image that is used to test the publish functionality
        assert (
            build_image(
                path=TESTS_RESOURCES_DIR,
                dockerfile=LOCAL_IMAGE_DOCKERFILE,
                tag=LOCAL_IMAGE_NAME,
            )
            is True
        )

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory and its contents
        assert remove(CURRENT_TEST_DIR, recursive=True) is True
        assert not exists(CURRENT_TEST_DIR)
        assert remove_image(LOCAL_IMAGE_NAME) is True

    # TODO, this test is not working because it needs either a
    # valid or mock registry to test the publish to registry functionality
    # def test_publish_image_to_registry(self):
    #     self.assertTrue(
    #         publish(
    #             f"{LOCAL_REGISTRY}/{TEST_PUBLISH_CONTAINER_IMAGE}",
    #             TEST_PUBLISH_DESTINATION,
    #             PublishTypes.CONTAINER_IMAGE_REGISTRY,
    #         )
    #     )

    def test_publish_image_to_archive(self):
        publish_destination = os.path.join(
            self.publish_directory,
            f"{TEST_PUBLISH_CONTAINER_IMAGE}.{ARCHIVE_EXTENSION}-1",
        )
        self.assertTrue(
            publish(
                f"{LOCAL_REGISTRY}/{TEST_PUBLISH_CONTAINER_IMAGE}",
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
        publish_checksum_destination = f"{publish_destination}.{CHECKSUM_ALGORITHM}"
        self.assertTrue(
            publish(
                f"{LOCAL_REGISTRY}/{TEST_PUBLISH_CONTAINER_IMAGE}",
                publish_destination,
                PublishTypes.CONTAINER_IMAGE_ARCHIVE,
                with_checksum=True,
                checksum_algorithm=CHECKSUM_ALGORITHM,
            )
        )
        self.assertTrue(exists(publish_destination))
        self.assertTrue(exists(publish_checksum_destination))
        self.assertEqual(
            hashsum(publish_destination, algorithm=CHECKSUM_ALGORITHM),
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
                f"{LOCAL_REGISTRY}/{TEST_PUBLISH_CONTAINER_IMAGE}",
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
