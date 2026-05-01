from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from xania.web.routes import router


_stack = ExitStack()


def _static_dir() -> Path:
    """
    Materialize packaged `xania/static/` as a real directory path.

    FastAPI's StaticFiles requires a filesystem path; `importlib.resources`
    provides a temporary path for wheel installs.
    """
    from importlib.resources import as_file, files

    static_root = files("xania").joinpath("static")
    return _stack.enter_context(as_file(static_root))


def create_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    app.mount("/static", StaticFiles(directory=str(_static_dir())), name="static")
    app.include_router(router)
    return app


app = create_app()


__all__ = ["app", "create_app"]

