from abc import ABC, abstractmethod
from datetime import datetime

class IClock(ABC):

    @abstractmethod
    def now(self) -> datetime:
        pass