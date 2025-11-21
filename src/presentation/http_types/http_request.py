
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(slots=True)
class HttpRequest:
    method: str
    url: str
    headers: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Any] = None
    query_params: Dict[str, Any] = field(default_factory=dict)
    ipv4: Optional[str] = None
    path_params: Dict[str, Any] = field(default_factory=dict)
    refresh_token: Optional[str] = None
    cookies: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"HttpRequest("
            f"method={self.method}, "
            f"url={self.url}, "
            f"headers={self.headers}, "
            f"body={self.body})"
        )