from src.shared.infrastructure.persistence.neo4j.migrations.run import split_cypher_statements


def test_split_cypher_statements_ignores_empty_segments() -> None:
    source = "CREATE INDEX first IF NOT EXISTS FOR (n:Node) ON (n.id);\n\n; CREATE INDEX second IF NOT EXISTS FOR (n:Node) ON (n.name);"

    assert split_cypher_statements(source) == (
        "CREATE INDEX first IF NOT EXISTS FOR (n:Node) ON (n.id)",
        "CREATE INDEX second IF NOT EXISTS FOR (n:Node) ON (n.name)",
    )
