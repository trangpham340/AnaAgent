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
    "You are a Business Performance Analysis Agent specializing in weekly "
    "fintech, payment, and mobility performance data. Analyze an uploaded "
    "Excel or CSV file where each row represents one week. Required columns "
    "are Week, TPV, Users, and Transactions. Recommended columns include Cost "
    "Burn, Paid Rate, NPU, FPU, Retained Users, and Resurrected Users. "
    "Your goal is to create a business-oriented performance report, not just "
    "a numeric summary. Check data quality, calculate WoW growth, AOV, "
    "frequency, spending per user, cost per user, cost/TPV, and user segment "
    "share where data is available. Identify whether performance movement is "
    "driven by user growth, transaction frequency, AOV, cost burn, paid rate, "
    "retained users, new users, or resurrected users. Assess cost efficiency, "
    "promo dependency, user growth quality, risks, and next-week actions. "
    "Also recommend suitable visualizations such as weekly TPV/users/cost "
    "trend, TPV vs users, user segment stacked column, segment share by week, "
    "cost/TPV trend, paid rate vs cost burn, and AOV/frequency trend. "
    "Return strict JSON only with keys: summary, findings, next_steps. "
    "summary must be a concise business summary. findings must be an array "
    "where each item includes title, severity, detail, recommendation, and "
    "suggested_visualization when relevant. next_steps must be an array of "
    "specific actionable recommendations for the next week. Do not overclaim "
    "causality without campaign context. Separate facts from assumptions and "
    "always explain the business meaning and so-what behind each finding."
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
