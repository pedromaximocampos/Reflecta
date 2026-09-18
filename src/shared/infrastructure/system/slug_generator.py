from slugify import slugify

from src.shared.domain.ports.system.islug_generator import ISlugGenerator


class SlugGenerator(ISlugGenerator):
    def generate_slug(self, text: str) -> str:
        return slugify(
            text,
            lowercase=True,
            separator="-",
            allow_unicode=False,
            algorithm="modern",
        )
