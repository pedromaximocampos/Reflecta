from dataclasses import dataclass
from datetime import datetime

from src.modules.catalog.public.author_id import AuthorId


@dataclass(eq=False, slots=True)
class Author:
    id: AuthorId
    name: str
    normalized_name: str
    description: str
    created_at: datetime
    updated_at: datetime | None = None
