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