from typing import Protocol, Any, Mapping


class ISESV2Client(Protocol):
    def send_email(self, **kwargs: Any) -> Mapping[str, Any]: ...