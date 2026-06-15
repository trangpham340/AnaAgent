import json

from openai import AsyncOpenAI

from app.core.config import Settings
from app.models.analysis import AnalysisRequest, AnalysisResponse, Finding


class AnalysisAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model = "gpt-4.1-mini"
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        if self.client is None:
            return self._fallback_analysis(request)

        prompt = self._build_prompt(request)
        response = await self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior AI project analysis agent. Return strict JSON with "
                        "keys: summary, findings, next_steps. Findings must include title, "
                        "severity, detail, recommendation."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        parsed = self._parse_json(response.output_text)
        return AnalysisResponse(
            project_name=request.project_name,
            summary=parsed["summary"],
            findings=[Finding(**finding) for finding in parsed["findings"]],
            next_steps=parsed["next_steps"],
            model_used=self.model,
            source="openai",
        )

    def _build_prompt(self, request: AnalysisRequest) -> str:
        return (
            f"Project: {request.project_name}\n\n"
            f"Content:\n{request.content}\n\n"
            f"Goals: {request.goals or ['Not specified']}\n"
            f"Constraints: {request.constraints or ['Not specified']}\n\n"
            "Analyze feasibility, risks, missing requirements, architecture concerns, "
            "delivery priorities, and recommended next actions."
        )

    def _parse_json(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("AI response was not valid JSON.") from exc

    def _fallback_analysis(self, request: AnalysisRequest) -> AnalysisResponse:
        return AnalysisResponse(
            project_name=request.project_name,
            summary=(
                "OPENAI_API_KEY is not configured. This deterministic fallback confirms "
                "the API is working and shows the expected response shape."
            ),
            findings=[
                Finding(
                    title="Missing AI provider key",
                    severity="medium",
                    detail="The application did not find OPENAI_API_KEY in the environment.",
                    recommendation="Add the real key to .env before using live AI analysis.",
                ),
                Finding(
                    title="Initial project review needed",
                    severity="low",
                    detail="The submitted content should be reviewed for goals, constraints, risks, and scope.",
                    recommendation="Provide detailed requirements and acceptance criteria for better analysis.",
                ),
            ],
            next_steps=[
                "Add OPENAI_API_KEY to .env.",
                "Send a representative project description to /api/v1/analyze.",
                "Review findings and convert accepted recommendations into implementation tasks.",
            ],
            model_used="fallback",
            source="local",
        )
