CREATE INDEX passage_status IF NOT EXISTS
FOR (passage:Passage)
ON (passage.status);

CREATE INDEX passage_work_status IF NOT EXISTS
FOR (passage:Passage)
ON (passage.work_id, passage.status);

CREATE INDEX passage_ingestion_status IF NOT EXISTS
FOR (passage:Passage)
ON (passage.ingestion_id, passage.status);
