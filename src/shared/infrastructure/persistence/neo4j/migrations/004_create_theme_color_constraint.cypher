CREATE CONSTRAINT theme_color_unique IF NOT EXISTS
FOR (theme:Theme)
REQUIRE theme.color IS UNIQUE;
