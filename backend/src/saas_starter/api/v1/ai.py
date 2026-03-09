"""AI endpoints: chat, summarize, analyze, usage."""

from typing import Annotated

from fastapi import APIRouter, Depends

from backend.src.saas_starter.ai import create_default_router
from backend.src.saas_starter.ai.features.analyze import AnalyzeFeature
from backend.src.saas_starter.ai.features.chat import ChatFeature
from backend.src.saas_starter.ai.features.summarize import SummarizeFeature
from backend.src.saas_starter.ai.router import LLMRouter
from backend.src.saas_starter.api.deps import CurrentUser, DBSession
from backend.src.saas_starter.schemas.ai import (
    AnalyzeRequest,
    AnalyzeResponse,
    ChatRequest,
    ChatResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from backend.src.saas_starter.services.usage_service import get_usage_summary

router = APIRouter(prefix="/ai", tags=["ai"])


def get_llm_router() -> LLMRouter:
    """Dependency that provides the LLM router (overridable in tests)."""
    return create_default_router()


LLMDep = Annotated[LLMRouter, Depends(get_llm_router)]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    user: CurrentUser,
    db: DBSession,
    llm: LLMDep,
) -> ChatResponse:
    """Chat with an AI model."""
    feature = ChatFeature(llm)
    response = await feature.complete(
        messages=req.messages,
        model=req.model,
        tenant_id=user.tenant_id,
        user_id=user.id,
        db=db,
    )
    return ChatResponse(
        content=response.content,
        usage={
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": str(response.cost_usd),
            "model": response.model,
        },
    )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(
    req: SummarizeRequest,
    user: CurrentUser,
    db: DBSession,
    llm: LLMDep,
) -> SummarizeResponse:
    """Summarize text."""
    feature = SummarizeFeature(llm)
    response = await feature.summarize(
        text=req.text,
        style=req.style,
        model=req.model,
        tenant_id=user.tenant_id,
        user_id=user.id,
        db=db,
    )
    return SummarizeResponse(
        summary=response.content,
        usage={
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": str(response.cost_usd),
            "model": response.model,
        },
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    req: AnalyzeRequest,
    user: CurrentUser,
    db: DBSession,
    llm: LLMDep,
) -> AnalyzeResponse:
    """Analyze text."""
    feature = AnalyzeFeature(llm)
    response = await feature.analyze(
        text=req.text,
        analysis_type=req.analysis_type,
        model=req.model,
        tenant_id=user.tenant_id,
        user_id=user.id,
        db=db,
    )
    return AnalyzeResponse(
        result=response.content,
        usage={
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": str(response.cost_usd),
            "model": response.model,
        },
    )


@router.get("/usage")
async def usage(user: CurrentUser, db: DBSession) -> dict:
    """Get AI usage summary for the current tenant."""
    return await get_usage_summary(db=db, tenant_id=user.tenant_id)
