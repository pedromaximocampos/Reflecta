from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass

from src.infra.postgresql.models.users_model import UserModel
from src.infra.postgresql.models.auth_credentials_model import AuthCredentialsModel
from src.infra.postgresql.models.auth_sessions_model import AuthSessionsModel