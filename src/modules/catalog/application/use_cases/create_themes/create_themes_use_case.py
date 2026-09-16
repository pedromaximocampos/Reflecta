from shared.domain.ports.system.iulid_generator import IULIDGenerator
from src.modules.catalog.application.use_cases.create_themes.dto import CreateThemesInputDTO, CreateThemesOutputDTO
from src.modules.catalog.application.use_cases.create_themes.icreate_themes_use_case import ICreateThemesUseCase


class CreateThemesUseCase(ICreateThemesUseCase):
    def __init__(self, theme_repository, ulid_generator: IULIDGenerator):
        self.theme_repository = theme_repository
        self.ulid_generator = ulid_generator

    async def execute(self, themes_input: CreateThemesInputDTO) -> CreateThemesOutputDTO:
        created_themes = []
        for theme_data in themes_input.themes:
            theme_data.id = self.ulid_generator.generate_ulid()
            created_theme = self.theme_repository.create(theme_data)
            created_themes.append(created_theme)
        return CreateThemesOutputDTO.to_class(themes=created_themes)