from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PostgresqlSettings:
    host: str
    port: int
    db_name: str
    user: str
    password: str
    ssl: bool
    driver: str = "asyncpg"
    echo: bool = False
    app_name: str = "individuum-app"
    pool_size: int = 3
    max_overflow: int = 2
    pool_timeout_seconds: int = 15
    pool_recycle_seconds: int = 600
    command_timeout_seconds: int = 30

    @property
    def connection_string(self) -> str:
        ssl_mode = "require" if self.ssl else "disable"
        return (
            f"postgresql+{self.driver}://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.db_name}"
        )
