from src.modules.ai_processing.application.ports.analysis import IWorkPassageAnalyzer
from src.modules.ai_processing.infrastructure.analysis import OpenAIWorkPassageAnalyzer
from src.modules.ai_processing.infrastructure.openai_interpreter import OpenAISettings


def get_work_passage_analyzer() -> IWorkPassageAnalyzer:
    analyzer = OpenAIWorkPassageAnalyzer(OpenAISettings())
    analyzer.ensure_available()
    return analyzer
