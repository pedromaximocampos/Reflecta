from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PassageId:
    value: str
