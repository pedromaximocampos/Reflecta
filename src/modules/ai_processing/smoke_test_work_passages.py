"""Run one paid, isolated work-passage analysis request."""

import asyncio
import json

from src.modules.ai_processing.infrastructure.analysis import (
    OpenAIWorkPassageAnalyzer,
)
from src.modules.ai_processing.infrastructure.openai_interpreter import (
    OpenAISettings,
)
from src.modules.catalog.public.analysis_theme import ThemeOption
from src.modules.catalog.public.work_id import WorkId


async def main() -> int:
    analyzer = OpenAIWorkPassageAnalyzer(OpenAISettings())
    analyzer.ensure_available()
    result = await analyzer.analyze(
        work_id=WorkId("smoke-test-work"),
        chunk_text=(
            "Ao enfrentar uma decisão difícil, Helena interrompeu a pressa e "
            "observou quais consequências dependiam de suas escolhas. Ela não "
            "podia controlar a reação das outras pessoas, mas podia agir com "
            "honestidade, atenção e responsabilidade diante do que sabia."
        ),
        themes=(
            ThemeOption(
                id="smoke-test-responsibility",
                slug="responsabilidade",
                label="Responsabilidade",
                description="Escolhas conscientes e suas consequências.",
            ),
        ),
    )
    print(
        json.dumps(
            {
                "passages": [
                    {
                        "exact_text": passage.exact_text,
                        "paraphrase": passage.paraphrase,
                        "rationale": passage.rationale,
                        "themes": [
                            {
                                "theme_id": theme.theme_id,
                                "confidence": theme.confidence,
                            }
                            for theme in passage.themes
                        ],
                    }
                    for passage in result.passages
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
