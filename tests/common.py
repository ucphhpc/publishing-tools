# Copyright (C) 2024  The publishing-tools Project by the Science HPC Center at UCPH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

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
