"""
Example: Running a compiled Xania SPA on FastAPI

There are two ways to serve a compiled SPA:

1. CLI (simplest):
   xania serve ./documentation

2. Python (for custom backends):
   See below
"""

from pathlib import Path
from fastapi import FastAPI
from xania.web.serve import mount_spa

# ============================================================================
# Pattern 1: Minimal SPA Server
# ============================================================================
def create_spa_app(spa_dir: str | Path = "documentation") -> FastAPI:
    """Create a FastAPI app that serves a compiled SPA."""
    app = FastAPI()
    mount_spa(app, spa_dir)
    return app


# ============================================================================
# Pattern 2: SPA + Custom API Routes
# ============================================================================
def create_spa_with_api(spa_dir: str | Path = "documentation") -> FastAPI:
    """Create a FastAPI app with both SPA and custom API endpoints."""
    app = FastAPI()
    
    # Add custom API routes first
    @app.get("/api/hello")
    def hello():
        return {"message": "Hello from API!"}
    
    @app.get("/api/data")
    def data():
        return {"items": [1, 2, 3, 4, 5]}
    
    # Then mount the SPA (so /api routes take precedence)
    mount_spa(app, spa_dir)
    
    return app


# ============================================================================
# Usage
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    
    # Choose one:
    # app = create_spa_app()                    # Just SPA
    app = create_spa_with_api()                 # SPA + API
    
    print("🚀 Starting server...")
    print("📍 http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
