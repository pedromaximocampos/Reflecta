from typing import Protocol


class ISlugGenerator(Protocol):
    """Interface para gerar slugs a partir de strings."""

    def generate_slug(self, text: str) -> str:
        """Gera um slug a partir do texto fornecido."""
        ...
