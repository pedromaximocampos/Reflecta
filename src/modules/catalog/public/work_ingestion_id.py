from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkIngestionId:
    value: str
