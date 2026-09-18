from dataclasses import dataclass
from datetime import datetime, timezone

from src.modules.catalog.public.theme_id import ThemeId


@dataclass(eq=False, slots=True)
class Theme:
    id: ThemeId
    slug: str
    label: str
    description: str
    created_at: datetime
    is_active: bool = True
    updated_at: datetime | None = None



    def activate(self, updated_at: datetime | None = None) -> None:
        self.is_active = True

        self.updated_at = self.__check_timestamp(updated_at)

    def deactivate(self, updated_at: datetime | None = None) -> None:
        self.is_active = False

        self.updated_at = self.__check_timestamp(updated_at)

    def update(
        self,
        updated_at: datetime | None = None,
        label: str | None = None,
        description: str | None = None,
    ) -> None:
        self.updated_at = self.__check_timestamp(updated_at)

        if label is not None:
            self.label = label

        if description is not None:
            self.description = description

    @staticmethod
    def __check_timestamp(timestamp: datetime | None) -> datetime:
        if timestamp is None:
            return datetime.now(timezone.utc)
        return timestamp
