CREATE CONSTRAINT theme_id_unique IF NOT EXISTS
FOR (theme:Theme)
REQUIRE theme.theme_id IS UNIQUE;

CREATE CONSTRAINT theme_slug_unique IF NOT EXISTS
FOR (theme:Theme)
REQUIRE theme.slug IS UNIQUE;