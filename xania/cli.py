from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
import shutil
import sys
from typing import Optional

import click


@dataclass(frozen=True)
class CliConfig:
    default_app: str = "xania.web.app:app"


def _run_uvicorn(app: str, host: str, port: int, reload: bool) -> None:
    try:
        import uvicorn

        uvicorn.run(app, host=host, port=int(port), reload=reload)
    except Exception as e:  # pragma: no cover
        raise click.ClickException(f"Failed to start server: {e}") from e


def _write_spa_index_html(dest: Path, *, title: str, tailwind: bool) -> None:
    tw = '    <script src="https://cdn.tailwindcss.com"></script>\n' if tailwind else ""
    html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
{tw}  </head>
  <body>
    <div id="app"></div>
    <script src="/static/spa_runtime.js"></script>
    <script src="/static/app.js"></script>
  </body>
</html>
"""
    dest.write_text(html, encoding="utf-8")


def _copy_package_static(out_dir: Path) -> None:
    """
    Copy packaged static assets into `out_dir/static`.

    Uses importlib.resources so it works when installed from a wheel.
    """
    from importlib.resources import as_file, files

    out_dir.mkdir(parents=True, exist_ok=True)
    dest_static = out_dir / "static"
    if dest_static.exists():
        shutil.rmtree(dest_static)

    static_root = files("xania").joinpath("static")
    with as_file(static_root) as static_path:
        shutil.copytree(static_path, dest_static)


@click.group(invoke_without_command=True)
@click.option("--app", "app_path", default=None, help="ASGI app path, e.g. module:app")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
@click.pass_context
def cli(ctx: click.Context, app_path: Optional[str], host: str, port: int) -> None:
    """Xania CLI — Python UI framework for building SPAs."""
    if ctx.invoked_subcommand is not None:
        return
    cfg = CliConfig()
    _run_uvicorn(app_path or cfg.default_app, host=host, port=port, reload=False)


@cli.command("init")
@click.argument("project_name", default="my_spa")
def init(project_name: str) -> None:
    """Create a new Xania SPA project.
    
    Example:
        xania init my_website
    """
    project_path = Path.cwd() / project_name
    
    if project_path.exists():
        raise click.ClickException(f"Directory {project_name} already exists")
    
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create main app file
    app_py = project_path / "app.py"
    app_py.write_text('''"""
My Xania Website

Development server with hot reload:
    xania dev

Build static files:
    python app.py compile

Then serve static files:
    xania serve .
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from xania.runtime.spa import SpaApp, StaticPage
from xania.renderer.elements import (
    Div, Nav, H1, P, A, Style, Script, Section
)
from xania.runtime.compiler import SpaCompiler

# Create your SPA
spa = SpaApp(
    name="MySite",
    root_id="app",
)

# Define shared styles using Style() element
shared_styles = Style("""
:root {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --dark-bg: #0f172a;
    --dark-card: #1e293b;
    --text-primary: #ffffff;
    --text-secondary: #94a3b8;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    background: linear-gradient(135deg, var(--dark-bg), var(--dark-card));
    color: var(--text-primary);
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6;
}

.container {
    max-width: 48rem;
    margin: 0 auto;
    padding: 2rem;
}

nav {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

a {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: var(--primary);
    color: white;
    text-decoration: none;
    border-radius: 0.5rem;
    transition: background 0.3s;
}

a:hover {
    background: var(--primary-hover);
}

h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    font-weight: bold;
}

p {
    color: var(--text-secondary);
    margin-bottom: 1rem;
}
""")

# Define interaction script using Script() element
interaction_script = Script("""
document.addEventListener('DOMContentLoaded', () => {
    console.log('✨ Xania page loaded!');
    console.log('No raw HTML needed - everything is built with Python!');
    
    // Add click feedback
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            console.log('Navigating to:', link.href);
        });
    });
});
""")

# Build home page using element functions
home_page = Div(
    shared_styles,
    Section(
        H1("Welcome to Xania"),
        P("A Python UI framework for building SPAs"),
        P("No raw HTML strings needed! Everything is built with Python functions."),
        Nav(
            A("Home", href="/"),
            A("About", href="/about"),
        ),
        class_="container"
    ),
    interaction_script,
)

# Build about page using element functions
about_page = Div(
    shared_styles,
    Section(
        H1("About"),
        P("This is a Xania website built with Python element functions!"),
        P("See HTML_ELEMENTS.md in the docs for examples of using Script() and Style()."),
        P("Edit app.py to customize your site, then save and the server will hot-reload."),
        Nav(
            A("← Back to Home", href="/"),
        ),
        class_="container"
    ),
    interaction_script,
)

# Add routes to SPA
spa.route("/", StaticPage(title="Home", html=home_page.render()))
spa.route("/about", StaticPage(title="About", html=about_page.render()))

# FastAPI development server
application = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Mount Xania static files (from installed package)
from importlib.resources import as_file, files as pkg_files
try:
    xania_static = pkg_files("xania").joinpath("static")
    with as_file(xania_static) as static_path:
        application.mount("/static", StaticFiles(directory=str(static_path)), name="static")
except:
    pass  # Static files optional in dev

# Serve SPA pages with hot reload support
from fastapi.responses import HTMLResponse

@application.get("/", response_class=HTMLResponse)
async def root():
    return home_page.render()

@application.get("/about", response_class=HTMLResponse)
async def about():
    return about_page.render()

@application.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_fallback(full_path: str):
    # Fallback to home for unmatched routes (SPA routing)
    return home_page.render()

# Export as 'app' for xania dev
app = application

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "compile":
        # Compile to static files
        compiler = SpaCompiler(title="My Website", tailwind=False)
        compiler.write(spa, Path.cwd())
        print("✅ Website compiled! Run: xania serve .")
    else:
        # Run dev server
        import uvicorn
        uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
''', encoding="utf-8")
    
    # Create README
    readme = project_path / "README.md"
    readme.write_text(f"""# {project_name.title()}

A Xania website.

## Quick Start

**Development with hot reload:**
```bash
xania dev
```

Then open: http://127.0.0.1:8000

Edit `app.py` and save - the server will hot-reload automatically!

## Build for Production

To create static files:
```bash
python app.py compile
```

This generates:
- `index.html`
- `static/app.js`
- `static/spa_runtime.js`

Then serve with:
```bash
xania serve .
```

## Customize Your Site

- Edit `app.py` to add pages and change content
- Modify styles, add routes, customize components
- Save and hot-reload will update your browser instantly

## Deploy

Copy the generated files (`index.html` + `static/`) to any static hosting:
- Netlify
- Vercel  
- GitHub Pages
- AWS S3
- Any web server

## Learn More

Visit: https://github.com/xania/framework
""", encoding="utf-8")
    
    click.echo(f"✅ Created project: {project_name}/")
    click.echo("")
    click.echo("Next steps:")
    click.echo(f"  cd {project_name}")
    click.echo("  xania dev              # Start with hot reload")


@cli.command("dev")
@click.option("--app", "app_path", default=None, help="ASGI app path, e.g. module:app")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
@click.option("--reload/--no-reload", default=True, show_default=True)
def dev(app_path: Optional[str], host: str, port: int, reload: bool) -> None:
    """Run a development server (uvicorn --reload by default)."""
    cfg = CliConfig()
    
    # If no app specified, try to use local app.py in current directory
    if app_path is None:
        cwd = Path.cwd()
        local_app = cwd / "app.py"
        if local_app.exists():
            app_path = "app:app"
            # Set PYTHONPATH for the subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
            
            # Run uvicorn as a subprocess with the updated environment
            cmd = [
                sys.executable, "-m", "uvicorn",
                app_path,
                "--host", host,
                "--port", str(port),
            ]
            if reload:
                cmd.append("--reload")
            
            subprocess.run(cmd, env=env)
            return
        else:
            app_path = cfg.default_app
    
    _run_uvicorn(app_path, host=host, port=port, reload=reload)


@cli.command("build")
@click.option("--out", default="dist", show_default=True, type=click.Path(path_type=Path))
@click.option("--title", default="Xania App", show_default=True)
@click.option("--tailwind/--no-tailwind", default=True, show_default=True)
def build(out: Path, title: str, tailwind: bool) -> None:
    """Write `index.html` + `static/` for static hosting."""
    out = out.resolve()
    _copy_package_static(out)
    _write_spa_index_html(out / "index.html", title=title, tailwind=tailwind)
    click.echo(f"Wrote static site to {out}")


@cli.command("serve")
@click.argument("spa_dir", type=click.Path(exists=True, path_type=Path), required=False, default=Path.cwd())
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
def serve(spa_dir: Path, host: str, port: int) -> None:
    """Serve a compiled Xania SPA on a FastAPI server.
    
    Example:
        xania serve ./dist
        xania serve ./documentation --port 9000
    """
    spa_path = spa_dir.resolve()
    index_html = spa_path / "index.html"
    static_dir = spa_path / "static"
    
    if not index_html.exists():
        raise click.ClickException(f"index.html not found in {spa_path}")
    if not static_dir.exists():
        raise click.ClickException(f"static/ directory not found in {spa_path}")
    
    # Create a minimal FastAPI app that serves the SPA
    try:
        import uvicorn
        from fastapi import FastAPI
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import HTMLResponse
        
        app = FastAPI()
        
        # Mount static files
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Serve index.html with history API fallback
        @app.get("/{full_path:path}", response_class=HTMLResponse)
        def spa_fallback(full_path: str) -> str:
            # Skip static assets
            if full_path.startswith("static/"):
                return "Not Found"
            return index_html.read_text(encoding="utf-8")
        
        @app.get("/", response_class=HTMLResponse)
        def spa_root() -> str:
            return index_html.read_text(encoding="utf-8")
        
        click.echo(f"🚀 Serving SPA from {spa_path}")
        click.echo(f"📍 http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)
    except Exception as e:
        raise click.ClickException(f"Failed to start server: {e}") from e


@cli.command("help")
def help_cmd() -> None:
    """Print a quick-start guide."""
    click.echo(
        "\n".join(
            [
                "╔════════════════════════════════════════╗",
                "║  Xania — Python UI Framework           ║",
                "╚════════════════════════════════════════╝",
                "",
                "📦 Creating a new website:",
                "  xania init my_website",
                "  cd my_website",
                "  python app.py              # Compile to static files",
                "  xania serve .              # Run on http://127.0.0.1:8000",
                "",
                "🚀 Running an existing website:",
                "  xania serve ./my_website",
                "",
                "🛠️  Development:",
                "  xania dev                           # Run FastAPI dev server",
                "  xania dev --app yourproj.web:app    # Custom app",
                "",
                "📦 Building (for static hosting):",
                "  xania build --out dist              # Generate static files",
                "",
                "💡 Workflow:",
                "  1. Create project: xania init my_site",
                "  2. Edit app.py with your pages",
                "  3. Compile: python app.py",
                "  4. Run: xania serve .",
                "  5. Deploy: Copy static files to hosting",
                "",
                "📚 Examples:",
                "  - See documentation/ for a full tutorial SPA",
                "  - Run: xania serve documentation",
            ]
        )
    )


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    cli.main(args=argv, prog_name="xania")


__all__ = ["cli", "main"]

