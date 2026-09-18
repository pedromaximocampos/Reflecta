from src.shared.config.settings import get_settings
from src.shared.infrastructure.persistence.neo4j.configs.settings import Neo4jConfig
from src.shared.infrastructure.persistence.neo4j.connection import Neo4jConnectionHandler

settings = get_settings()


neo4j_settings = Neo4jConfig(
    uri=settings.NEO4J_URI,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD,
    database=settings.NEO4J_DATABASE,
    encrypted=settings.NEO4J_ENCRYPTED,
)
reflecta_neo4j_provider = Neo4jConnectionHandler(settings=neo4j_settings)
