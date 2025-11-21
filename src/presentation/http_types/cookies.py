from dataclasses import dataclass
from typing import Optional


@dataclass
class Cookie:
    name: str
    value: str
    max_age: Optional[int] = None
    http_only: bool = True
    secure: bool = True
    samesite: str = "lax"
    path: str = "/"
    domain: Optional[str] = None