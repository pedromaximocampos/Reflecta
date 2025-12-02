import pytest
from unittest.mock import Mock
from src.domain.exceptions.api_types import AuthError

class TestLogoffUseCase:


    @pytest.mark.asyncio
    async def test_logoff_should_invalidate_session(self, logoff_ctx):
        # Arrange
        logoff_ctx.auth_service.validate_session_by_refresh_token.return_value = logoff_ctx.auth_session

        # Act
        await logoff_ctx.use_case.execute(refresh_token="test_refresh_token")

        # Assert
        logoff_ctx.auth_service.validate_session_by_refresh_token.assert_awaited_once_with("test_refresh_token")
        logoff_ctx.auth_service.invalidate_session.assert_awaited_once_with(logoff_ctx.auth_session.id)


    @pytest.mark.asyncio
    async def test_logoff_should_raise_auth_error_for_invalid_refresh_token(self, logoff_ctx):
        # Arrange
        logoff_ctx.auth_service.validate_session_by_refresh_token.return_value = None

        # Act & Assert
        with pytest.raises(AuthError) as exc_info:
            await logoff_ctx.use_case.execute(refresh_token="invalid_refresh_token")

        assert str(exc_info.value) == "Sessão inválida ou expirou."
        logoff_ctx.auth_service.validate_session_by_refresh_token.assert_awaited_once_with("invalid_refresh_token")
        logoff_ctx.auth_service.invalidate_session.assert_not_awaited()