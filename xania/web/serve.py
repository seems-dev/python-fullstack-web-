"""
SPA serving utilities for FastAPI.

Provides easy way to serve compiled SPAs built with Xania.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse


def mount_spa(app: FastAPI, spa_dir: Path | str, *, mount_at: str = "/") -> None:
    """
    Mount a compiled Xania SPA into a FastAPI app.
    
    Serves `index.html` for all routes (history API fallback) and 
    static files from the `static/` subdirectory.
    
    Args:
        app: FastAPI application
        spa_dir: Path to compiled SPA directory (contains index.html + static/)
        mount_at: URL path to mount at (default: "/")
    
    Example:
        ```python
        from fastapi import FastAPI
        from xania.web.serve import mount_spa
        
        app = FastAPI()
        mount_spa(app, Path("documentation"))
        ```
    """
    spa_path = Path(spa_dir).resolve()
    index_html = spa_path / "index.html"
    static_dir = spa_path / "static"
    
    if not index_html.exists():
        raise FileNotFoundError(f"index.html not found in {spa_path}")
    if not static_dir.exists():
        raise FileNotFoundError(f"static/ not found in {spa_path}")
    
    # Mount static files
    static_url = mount_at.rstrip("/") + "/static" if mount_at != "/" else "/static"
    app.mount(static_url, StaticFiles(directory=str(static_dir)), name="spa_static")
    
    # Serve index.html with history API fallback
    @app.get(mount_at + "{full_path:path}", response_class=HTMLResponse)
    def spa_fallback(full_path: str) -> str:
        # Skip static assets and API paths
        if full_path.startswith("static/") or full_path.startswith("api/"):
            return "Not Found"
        return index_html.read_text(encoding="utf-8")
    
    # Also serve root path
    @app.get(mount_at.rstrip("/") or "/", response_class=HTMLResponse)
    def spa_root() -> str:
        return index_html.read_text(encoding="utf-8")


__all__ = ["mount_spa"]
