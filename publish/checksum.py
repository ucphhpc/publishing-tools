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

from publish.utils.io import hashsum, write, exists, load
from publish.common import StrEnum


class ChecksumTypes(StrEnum):
    SHA256 = "sha256"
    SHA512 = "sha512"
    MD5 = "md5"


def checksum_file(path, algorithm=ChecksumTypes.SHA256):
    if not exists(path):
        return False
    return hashsum(path, algorithm=algorithm)


def write_checksum_file(path, destination=None, algorithm=ChecksumTypes.SHA256):
    checksum = checksum_file(path, algorithm=algorithm)
    if not checksum:
        return False
    if not destination:
        return write(path + f".{algorithm}", checksum)
    return write(destination, checksum)


def checksum_equal(path, checksum_file_path, algorithm=ChecksumTypes.SHA256):
    checksum = checksum_file(path, algorithm=algorithm)
    if not checksum:
        return False
    return checksum == load(checksum_file_path)
