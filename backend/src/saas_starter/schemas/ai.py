"""AI feature request/response schemas."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Chat completion request."""

    messages: list[dict]
    model: str = "gpt-4o-mini"


class ChatResponse(BaseModel):
    """Chat completion response."""

    content: str
    usage: dict


class SummarizeRequest(BaseModel):
    """Text summarization request."""

    text: str
    style: str = "concise"
    model: str = "gpt-4o-mini"


class SummarizeResponse(BaseModel):
    """Text summarization response."""

    summary: str
    usage: dict


class AnalyzeRequest(BaseModel):
    """Text analysis request."""

    text: str
    analysis_type: str = "general"
    model: str = "gpt-4o-mini"


class AnalyzeResponse(BaseModel):
    """Text analysis response."""

    result: str
    usage: dict
