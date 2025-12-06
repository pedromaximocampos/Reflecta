# tests/support/doubles/clock_fake.py
from datetime import datetime
from typing import Optional

from src.domain.ports.system.iclock import IClock


class ClockFake(IClock):
    """
    Fake de IClock para testes.

    - now() retorna um datetime fixo (configurável)
    - métodos de expiração retornam valores simples configuráveis
    """

    def __init__(
        self,
        now: Optional[datetime] = None,
        access_token_exp_seconds: int = 15 * 60,               # 15 min
        refresh_token_exp_seconds: int = 30 * 24 * 60 * 60,    # 30 dias
        email_verification_exp_seconds: int = 15 * 60,         # 15 min
    ) -> None:
        self._now = now or datetime.utcnow()
        self._access_token_exp_seconds = access_token_exp_seconds
        self._refresh_token_exp_seconds = refresh_token_exp_seconds
        self._email_verification_exp_seconds = email_verification_exp_seconds

        self.calls_now = 0

    def set_now(self, new_now: datetime) -> None:
        self._now = new_now

    def now(self) -> datetime:
        self.calls_now += 1
        return self._now

    def access_token_expiration_in_seconds(self) -> int:
        return self._access_token_exp_seconds

    def refresh_token_expiration_in_seconds(self) -> int:
        return self._refresh_token_exp_seconds

    def email_verification_code_expiration_in_seconds(self) -> int:
        return self._email_verification_exp_seconds
