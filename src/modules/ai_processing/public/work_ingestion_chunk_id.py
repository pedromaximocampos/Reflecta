from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkIngestionChunkId:
    value: str
