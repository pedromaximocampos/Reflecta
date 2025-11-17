from enum import Enum


class PasswordAlgorithm(str, Enum):
    ARGON2ID = "argon2id"
    BCRYPT = "bcrypt"