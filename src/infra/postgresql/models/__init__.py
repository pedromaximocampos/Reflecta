from src.infra.postgresql.configs.base import Base
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import BigInteger, String, Boolean, TIMESTAMP, func, ForeignKey, DATE
from src.infra.postgresql.models.auth_credentials_model import AuthCredentialsModel
from src.infra.postgresql.models.users_model import UserModel
from src.infra.postgresql.models.auth_sessions_model import AuthSessionsModel