from src.shared.config.settings import Settings


def test_database_url_uses_host_and_escapes_credentials() -> None:
    settings = Settings.model_construct(
        POSTGRES_HOST="reflecta.example.internal",
        POSTGRES_PORT=5432,
        POSTGRES_USER="reflecta_admin",
        POSTGRES_PASSWORD="p@ss:/word",
        POSTGRES_DB="reflecta",
    )

    assert settings.database_url == (
        "postgresql+asyncpg://reflecta_admin:p%40ss%3A%2Fword@"
        "reflecta.example.internal:5432/reflecta"
    )
