from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from example.counter import Counter
from renderer.registry import ComponentRegistry
from web.routes import router


def create_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    # Static runtime (no inline JS).
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Register example components.
    ComponentRegistry.register("Counter", Counter(id="counter"))

    # API routes.
    app.include_router(router)

    return app


app = create_app()

