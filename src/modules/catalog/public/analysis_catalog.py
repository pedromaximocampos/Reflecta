from src.modules.catalog.public.analysis_theme import ThemeOption
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)


class AnalysisThemeCatalog:
    def __init__(self, uow: ICatalogGraphUnitOfWork) -> None:
        self.uow = uow

    async def active_themes(self) -> tuple[ThemeOption, ...]:
        async with self.uow as uow:
            themes = await uow.theme_repository.list_themes()
            return tuple(
                ThemeOption(id=t.id.value, slug=t.slug, label=t.label, description=t.description)
                for t in themes if t.is_active
            )
