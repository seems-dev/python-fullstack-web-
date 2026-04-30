from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class EventRequest(BaseModel):
    component: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)


class Update(BaseModel):
    id: str = Field(..., min_length=1)
    html: str


class EventResponse(BaseModel):
    updates: List[Update]


__all__ = ["EventRequest", "Update", "EventResponse"]

