import os

BASE_TESTS_PATH = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_PATH = os.path.join(BASE_TESTS_PATH, "tmp")
TESTS_RESOURCES_DIR = os.path.join(BASE_TESTS_PATH, "res")
TESTS_DOCKERFILE = os.path.join(TESTS_RESOURCES_DIR, "Dockerfile")

# Local registry settings
LOCAL_REGISTRY = "localhost"
LOCAL_OWNER = "test"

# Various test settings
ARCHIVE_EXTENSION = "tar"
NON_EXISTING_FILE = "non_existing_file"
NON_EXISTING_IMAGE = "non_existing_image"
NON_EXISTING_DESTINATION = "non_existing_destination"
NON_EXISTING_KEY = "non_existing_key"
TEST_FILE = "test_file"
TEST_CONTENT = "sfopawmdioamwioac aoimaw aw 2414 14 foobar"
