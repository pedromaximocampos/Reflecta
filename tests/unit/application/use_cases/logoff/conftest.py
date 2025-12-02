from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock
import pytest
from src.application.use_cases.logoff.logoff_use_case_impl import LogoffUseCaseImpl


@dataclass
class LogoffTestContext:
    use_case: 'LogoffUseCaseImpl'
    auth_service: AsyncMock
    auth_session: Mock

@pytest.fixture
def logoff_ctx(logoff_use_case_with_mocks: LogoffUseCaseImpl, mock_auth_session_service, mock_auth_session) -> LogoffTestContext:
    return LogoffTestContext(
        use_case=logoff_use_case_with_mocks,
        auth_service=mock_auth_session_service,
        auth_session=mock_auth_session
    )

@pytest.fixture
def logoff_use_case_with_mocks(mock_auth_session_service) -> LogoffUseCaseImpl:
    return LogoffUseCaseImpl(
        auth_session_service=mock_auth_session_service,
    )



