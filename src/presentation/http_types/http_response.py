from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.presentation.http_types.cookies import Cookie


@dataclass
class HttpResponse:
    status_code: int
    body: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: List[Cookie] = field(default_factory=list)