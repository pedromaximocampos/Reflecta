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
    max_connection_pool_size=settings.NEO4J_MAX_CONNECTION_POOL_SIZE,
    connection_acquisition_timeout_seconds=settings.NEO4J_CONNECTION_ACQUISITION_TIMEOUT_SECONDS,
    connection_timeout_seconds=settings.NEO4J_CONNECTION_TIMEOUT_SECONDS,
    max_connection_lifetime_seconds=settings.NEO4J_MAX_CONNECTION_LIFETIME_SECONDS,
)
reflecta_neo4j_provider = Neo4jConnectionHandler(settings=neo4j_settings)
