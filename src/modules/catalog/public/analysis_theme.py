from pydantic import BaseModel, ConfigDict


class ThemeOption(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    id: str
    slug: str
    label: str
    description: str
