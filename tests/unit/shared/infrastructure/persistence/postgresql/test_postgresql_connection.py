from unittest.mock import patch

from src.shared.infrastructure.persistence.postgresql.configs.settings import (
    PostgresqlSettings,
)
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler


def test_postgresql_engine_uses_bounded_pool_and_timeouts() -> None:
    settings = PostgresqlSettings(
        host="localhost",
        port=5432,
        db_name="reflecta",
        user="reflecta",
        password="secret",
        ssl=False,
    )

    with patch(
        "src.shared.infrastructure.persistence.postgresql.connection.create_async_engine"
    ) as create_engine:
        DBConnectionHandler(settings)

    options = create_engine.call_args.kwargs
    assert options["pool_size"] == 3
    assert options["max_overflow"] == 2
    assert options["pool_timeout"] == 15
    assert options["pool_recycle"] == 600
    assert options["pool_pre_ping"] is True
    assert options["connect_args"]["command_timeout"] == 30
    assert options["connect_args"]["server_settings"]["application_name"] == "individuum-app"
