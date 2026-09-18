from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Neo4jConfig:
    uri: str
    user: str
    password: str
    database: str
    encrypted: bool = True