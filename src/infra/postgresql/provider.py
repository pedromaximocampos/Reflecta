import ssl

from src.infra.postgresql.configs.settings import PostgresqlSettings
from src.infra.postgresql.connection import DBConnectionHandler

from src.shared.globalvars import (
    LOCAL_PG_HOST,
    LOCAL_PG_PORT,
    LOCAL_PG_USER,
    LOCAL_PG_DATABASE,
    LOCAL_PG_PASSWORD
)

postgres_settings = PostgresqlSettings(
    user=LOCAL_PG_USER,
    password=LOCAL_PG_PASSWORD,
    host=LOCAL_PG_HOST,
    port=LOCAL_PG_PORT,
    db_name=LOCAL_PG_DATABASE,
    ssl=False,
    echo=True
)

individuum_mvp_provider = DBConnectionHandler(postgres_settings)