
from pydantic import BaseModel, ConfigDict, Field



class ThemeValidator(BaseModel):
    """Validator for creating a theme"""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., description="Theme name", min_length=3, max_length=50)
    description: str = Field(..., description="Theme description", min_length=3, max_length=255)
    is_active: bool = Field(..., description="Is theme active")

class CreateThemesValidator(BaseModel):
    """Validator for creating themes"""

    model_config = ConfigDict(extra="forbid")

    themes: list[ThemeValidator] = Field(..., description="List of themes to create", min_length=1)




class CreateThemesResponseValidator(BaseModel):
    """Validator for create themes response"""

    model_config = ConfigDict(extra="forbid")

    created_themes: list[ThemeValidator] = Field(..., description="List of created themes", min_length=1)