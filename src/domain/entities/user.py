from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from src.domain.ports.system.ulid_generator import IULIDGenerator
from src.domain.ports.system.clock import IClock


@dataclass(slots=True)
class User:
    id: str
    email: str
    username: str
    name: str
    date_of_birth: date
    created_at: datetime
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None

    @classmethod
    def create(cls, id_generator: IULIDGenerator, clock: IClock, email: str,
               username: str, name: str, date_of_birth: date, avatar_url: Optional[str] = None) -> 'User':
        return cls(
            id=id_generator.generate_ulid(),
            email=email,
            username=username,
            name=name,
            date_of_birth=date_of_birth,
            created_at=clock.now(),
            avatar_url=avatar_url
        )