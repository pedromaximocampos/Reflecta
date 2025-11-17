from abc import ABC, abstractmethod
from datetime import datetime

class IClock(ABC):

    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def access_token_expiration(self) -> int:
        pass

    @abstractmethod
    def refresh_token_expiration(self) -> int:
        pass