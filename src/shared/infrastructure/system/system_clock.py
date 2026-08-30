from src.shared.domain.ports.system.iclock import IClock
from datetime import datetime, timezone
from src.shared.config.settings import get_settings

_settings = get_settings()

class SystemClock(IClock):

    def access_token_expiration_in_seconds(self) -> int:
        return _settings.ACCESS_TOKEN_MINUTES * 60

    def refresh_token_expiration_in_seconds(self) -> int:
        return _settings.REFRESH_TOKEN_DAYS * 24 * 60 * 60

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def email_verification_code_expiration_in_seconds(self) -> int:
        return _settings.EMAIL_VERIFICATION_MINUTES * 60

    def password_reset_expiration_in_seconds(self) -> int:
        return _settings.RESET_PASSWORD_MINUTES * 60