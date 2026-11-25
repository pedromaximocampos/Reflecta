from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Neo4jConfig:
    uri: str
    user: str
    password: str
    database: str
    encrypted: bool = True
    max_connection_pool_size: int = 10
    connection_acquisition_timeout_seconds: int = 15
    connection_timeout_seconds: int = 10
    max_connection_lifetime_seconds: int = 600
