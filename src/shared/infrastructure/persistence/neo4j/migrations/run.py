"""Apply the idempotent Neo4j schema migrations bundled with the application."""

from pathlib import Path

from neo4j import GraphDatabase

from src.shared.config.settings import get_settings


MIGRATIONS_DIRECTORY = Path(__file__).resolve().parent


def split_cypher_statements(source: str) -> tuple[str, ...]:
    return tuple(statement.strip() for statement in source.split(";") if statement.strip())


def run_migrations() -> None:
    settings = get_settings()
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        encrypted=settings.NEO4J_ENCRYPTED,
    )
    try:
        driver.verify_connectivity()
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            for migration in sorted(MIGRATIONS_DIRECTORY.glob("[0-9][0-9][0-9]_*.cypher")):
                for statement in split_cypher_statements(migration.read_text(encoding="utf-8")):
                    session.run(statement).consume()
    finally:
        driver.close()


if __name__ == "__main__":
    run_migrations()
