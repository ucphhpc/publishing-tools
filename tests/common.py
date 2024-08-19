import os

BASE_TESTS_PATH = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_PATH = os.path.join(BASE_TESTS_PATH, "tmp")
TESTS_RESOURCES_DIR = os.path.join(BASE_TESTS_PATH, "res")
TESTS_DOCKERFILE = os.path.join(TESTS_RESOURCES_DIR, "Dockerfile")

# Local registry settings
LOCAL_REGISTRY = "localhost"
LOCAL_OWNER = "test"

# Test settings
TEST_CONTENT = "foo bar baz"
