from app.agents.analysis_agent import AnalysisAgent
from app.core.config import settings


def get_analysis_agent() -> AnalysisAgent:
    return AnalysisAgent(settings)
