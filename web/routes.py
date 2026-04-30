from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from engine.runtime import RuntimeConfig, html_shell
from renderer.registry import ComponentRegistry
from web.schemas import EventRequest, EventResponse, Update


router = APIRouter()

MOUNT_ACTION = "__mount__"


@router.get("/", response_class=HTMLResponse)
def index() -> str:
    # Client-side rendering: send only mount points + runtime.js.
    components = ComponentRegistry.all()
    return html_shell(components.items(), config=RuntimeConfig(title="Supreme", tailwind=True))


@router.post("/event", response_model=EventResponse)
def event(req: EventRequest) -> EventResponse:
    component = ComponentRegistry.get(req.component)

    # Important: no server requests are triggered automatically by state changes.
    # Only explicit App.dispatch() events call this endpoint.
    if req.action != MOUNT_ACTION:
        component.handle(req.action, req.payload)

    html = component.to_html()
    return EventResponse(updates=[Update(id=component.id, html=html)])


__all__ = ["router", "MOUNT_ACTION"]

