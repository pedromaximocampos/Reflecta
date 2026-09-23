import pytest
from unittest.mock import AsyncMock, Mock

from tests.support.contexts import LogoffTestContext
from src.modules.auth.application.use_cases.logoff.logoff_use_case_impl import LogoffUseCaseImpl


@pytest.fixture
def logoff_use_case_with_mocks(
    mock_auth_session_service: AsyncMock,
    mock_auth_unit_of_work,
) -> LogoffUseCaseImpl:
    return LogoffUseCaseImpl(
        auth_session_service=mock_auth_session_service,
        auth_unit_of_work=mock_auth_unit_of_work,
    )


@pytest.fixture
def logoff_ctx(
    logoff_use_case_with_mocks: LogoffUseCaseImpl,
    mock_auth_session_service: AsyncMock,
    mock_auth_unit_of_work,
    mock_auth_session: Mock,
) -> LogoffTestContext:
    ctx = LogoffTestContext(
        use_case=logoff_use_case_with_mocks,
        auth_session_service=mock_auth_session_service,
        auth_session=mock_auth_session,
    )
    # Alias para compatibilidade com os testes existentes
    ctx.auth_service = mock_auth_session_service
    ctx.uow = mock_auth_unit_of_work
    return ctx
