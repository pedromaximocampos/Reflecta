from pydantic import BaseModel, ConfigDict
from src.modules.catalog.public.theme_color import DEFAULT_THEME_COLOR, ThemeColor


class ThemeOption(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    id: str
    slug: str
    label: str
    description: str
    color: ThemeColor = DEFAULT_THEME_COLOR
