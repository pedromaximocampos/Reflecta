# src/domain/exceptions/api_types/__init__.py

from .bad_request_error import BadRequestError
from .authorization_error import AuthError
from .cache_error import CacheError
from .conflict_error import ConflictError
from .database_error import DatabaseError
from .forbidden_error import ForbiddenError
from .not_found_error import NotFoundError
from .upgrade_error import UpgradeRequired
from .user_is_not_admin import UserIsNotAdmin
from .validation_error import ValidationFailed

__all__ = [
    "BadRequestError",
    "AuthError",
    "CacheError",
    "ConflictError",
    "DatabaseError",
    "ForbiddenError",
    "NotFoundError",
    "UpgradeRequired",
    "UserIsNotAdmin",
    "ValidationFailed",
]
