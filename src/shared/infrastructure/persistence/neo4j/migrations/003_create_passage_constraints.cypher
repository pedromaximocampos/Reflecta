CREATE CONSTRAINT passage_id_unique IF NOT EXISTS
FOR (passage:Passage)
REQUIRE passage.passage_id IS UNIQUE;

CREATE CONSTRAINT passage_source_key_unique IF NOT EXISTS
FOR (passage:Passage)
REQUIRE passage.source_key IS UNIQUE;

CREATE INDEX passage_ingestion_chunk IF NOT EXISTS
FOR (passage:Passage)
ON (passage.ingestion_id, passage.source_chunk_id);
