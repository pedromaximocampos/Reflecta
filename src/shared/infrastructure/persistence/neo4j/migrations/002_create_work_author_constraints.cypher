CREATE CONSTRAINT work_id_unique IF NOT EXISTS
FOR (work:Work)
REQUIRE work.work_id IS UNIQUE;

CREATE CONSTRAINT work_slug_unique IF NOT EXISTS
FOR (work:Work)
REQUIRE work.slug IS UNIQUE;

CREATE CONSTRAINT author_id_unique IF NOT EXISTS
FOR (author:Author)
REQUIRE author.author_id IS UNIQUE;

CREATE CONSTRAINT author_normalized_name_unique IF NOT EXISTS
FOR (author:Author)
REQUIRE author.normalized_name IS UNIQUE;
