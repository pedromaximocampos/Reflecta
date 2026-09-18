from unittest.mock import patch

from src.shared.infrastructure.persistence.neo4j.configs.settings import Neo4jConfig
from src.shared.infrastructure.persistence.neo4j.connection import Neo4jConnectionHandler


def make_config(uri: str, encrypted: bool = True) -> Neo4jConfig:
    return Neo4jConfig(
        uri=uri,
        user="neo4j",
        password="test-password",
        database="neo4j",
        encrypted=encrypted,
    )


def test_plain_uri_passes_explicit_encryption_option_to_driver() -> None:
    with patch(
        "src.shared.infrastructure.persistence.neo4j.connection.AsyncGraphDatabase.driver"
    ) as driver:
        Neo4jConnectionHandler(make_config("bolt://localhost:7687", encrypted=False))

    assert driver.call_args.kwargs["encrypted"] is False


def test_secure_uri_does_not_duplicate_encryption_configuration() -> None:
    with patch(
        "src.shared.infrastructure.persistence.neo4j.connection.AsyncGraphDatabase.driver"
    ) as driver:
        Neo4jConnectionHandler(make_config("neo4j+s://example.databases.neo4j.io"))

    assert "encrypted" not in driver.call_args.kwargs
