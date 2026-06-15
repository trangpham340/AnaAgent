from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=10)
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    title: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    detail: str
    recommendation: str


class AnalysisResponse(BaseModel):
    project_name: str
    summary: str
    findings: list[Finding]
    next_steps: list[str]
    model_used: str
    source: str
