from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.shared.presentation.http_types.cookies import Cookie



@dataclass(slots=True)
class HttpResponse:
    status_code: int
    body: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: List[Cookie] = field(default_factory=list)

    def set_new_cookie(self, cookie: Cookie) -> None:
        """
        Adiciona um cookie à resposta, garantindo no máximo um cookie
        por (name, path, domain).
        """
        self.cookies = [
            c for c in self.cookies
            if not (
                c.name == cookie.name and
                c.path == cookie.path and
                c.domain == cookie.domain
            )
        ]
        self.cookies.append(cookie)