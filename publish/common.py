import sys

if sys.version_info.major == 3 and sys.version_info.minor < 11:
    from enum import Enum

    class StrEnum(str, Enum):
        pass

else:
    # https://docs.python.org/3/library/enum.html#enum.StrEnum
    # The StrEnum class was added in Python 3.11
    from enum import StrEnum
