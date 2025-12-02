from src.application.use_cases.login import LoginInput, LoginOutput
from src.domain.exceptions.custom_exceptions.email_verification_exceptions import EmailVerificationException
from tests.unit.application.use_cases.login.conftest import login_use_case_with_mocks
import pytest
from unittest.mock import Mock


class TestLoginUseCaseImpl:

    @pytest.mark.asyncio
    async def test_login_should_succeed_for_verified_user(self, login_ctx, login_input):
        # Arrange
        login_ctx.user_repo.find_by_email.return_value = login_ctx.user
        login_ctx.user.is_email_verified = True
        login_ctx.password_hasher.verify.return_value = True
        login_ctx.password_hasher.needs_rehash.return_value = False
        login_ctx.auth_session.create_session.return_value = Mock(
            access_token="access_token_123",
            refresh_token="refresh_token_456",
        )

        # Act
        result = await login_ctx.use_case.execute(login_input)

        # Assert – saída
        assert isinstance(result, LoginOutput)
        assert result.access_token == "access_token_123"
        assert result.refresh_token == "refresh_token_456"
        assert result.email.value == login_ctx.user.email.value
        assert result.user_id.value == login_ctx.user.id.value

        # Assert – interações básicas
        login_ctx.user_repo.find_by_email.assert_called_once_with(login_ctx.user.email)
        login_ctx.password_hasher.verify.assert_called_once()
        login_ctx.auth_session.create_session.assert_called_once_with(login_ctx.user)
        login_ctx.user.update_last_login.assert_called_once()
        login_ctx.user_repo.update_last_login_at.assert_called_once_with(login_ctx.user)

    @pytest.mark.asyncio
    async def test_login_should_raise_email_verification_exception_for_unverified_user(
            self,
            login_ctx,
            login_input,
    ):
        # Arrange
        login_ctx.user_repo.find_by_email.return_value = login_ctx.user
        login_ctx.password_hasher.verify.return_value = True
        login_ctx.user.is_email_verified = False
        login_ctx.email_verification.ensure_active_verification_for_user.side_effect = EmailVerificationException()

        # Act & Assert
        with pytest.raises(EmailVerificationException):
            await login_ctx.use_case.execute(login_input)

        # Garante que nada “andou” depois da exceção
        login_ctx.auth_session.create_session.assert_not_called()
        login_ctx.user_repo.update_auth_credentials.assert_not_called()
        login_ctx.user_repo.update_last_login_at.assert_not_called()