from typing import Protocol


class IULIDGenerator(Protocol):

    def generate_ulid(self) -> str: pass