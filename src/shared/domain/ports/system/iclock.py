from typing import Protocol
from datetime import datetime

class IClock(Protocol):

    def now(self) -> datetime:
        pass

    def access_token_expiration_in_seconds(self) -> int:
        pass

    def refresh_token_expiration_in_seconds(self) -> int:
        pass

    def email_verification_code_expiration_in_seconds(self) -> int:
        pass

    def password_reset_expiration_in_seconds(self) -> int:
        pass

    def user_deletion_expiration_in_seconds(self) -> int:
        pass

    def user_recovery_expiration_in_seconds(self) -> int:
        pass
