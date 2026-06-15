from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.analysis_agent import AnalysisAgent
from app.models.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import get_analysis_agent

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_project(
    request: AnalysisRequest,
    agent: AnalysisAgent = Depends(get_analysis_agent),
) -> AnalysisResponse:
    try:
        return await agent.analyze(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
