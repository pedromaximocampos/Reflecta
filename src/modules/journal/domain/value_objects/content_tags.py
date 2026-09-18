from enum import Enum
from typing import TypedDict

class TagCategory(str, Enum):
    PEOPLE = "people"
    PLACES = "places"
    DOMAINS = "domains"


class TagSource(str, Enum):
    USER = "user"
    AI = "ai"
    HEURISTIC = "heuristic"


class ContentTagItem(TypedDict, total=False):
    label: str
    source: TagSource
    confidence: float
    approved: bool


ContentTags = dict[str, list[ContentTagItem]]
