from enum import Enum


class Role(str, Enum):
    AUTHOR = "AUTHOR"
    APPROVER = "APPROVER"
