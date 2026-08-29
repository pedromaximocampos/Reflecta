# tests/support/contexts.py
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, Mock

from src.modules.auth.application.use_cases.login import LoginUseCaseImpl
from src.modules.auth.application.use_cases.logoff.logoff_use_case_impl import LogoffUseCaseImpl


@dataclass
class LoginTestContext:
    use_case: LoginUseCaseImpl
    user_repo: AsyncMock
    password_hasher: MagicMock
    clock: Mock
    auth_session_service: AsyncMock
    email_verification_service: AsyncMock
    user: Mock  # spec=User


@dataclass
class LogoffTestContext:
    use_case: LogoffUseCaseImpl
    auth_session_service: AsyncMock
    auth_session: Mock  # spec=AuthSession
