from typing import Protocol

from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.public.theme_id import ThemeId


class IThemeRepository(Protocol):
    async def get_theme_by_id(self, theme_id: ThemeId) -> Theme | None:
        """Retorna o tema associado ao ID fornecido."""
        ...

    async def create_theme(self, theme: Theme) -> Theme:
        """Cria um novo tema."""
        ...

    async def update_theme(self, theme: Theme) -> Theme:
        """Atualiza o tema especificado pelo ID."""
        ...

    async def delete_theme(self, theme_id: ThemeId) -> None:
        """Deleta o tema especificado pelo ID."""
        ...

    async def list_themes(self) -> list[Theme]:
        """Retorna uma lista de todos os temas."""
        ...

    async def create_many_themes(self, themes: list[Theme]) -> list[Theme]:
        """Cria vários temas de uma vez."""
        ...

    async def get_theme_by_slug(self, slug: str) -> Theme | None:
        """Retorna o tema associado ao slug fornecido."""
        ...
