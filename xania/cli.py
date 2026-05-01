from __future__ import annotations

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
    app_py.write_text("""\"\"\"
My Xania Website

Run this file to compile to static files:
    python app.py

Then serve with:
    xania serve .
\"\"\"

from pathlib import Path
from xania.runtime.spa import SpaApp, StaticPage, TemplatePage

# Create your SPA
app = SpaApp(
    name="MySite",
    root_id="app",
)

# Add pages
app.route(
    "/",
    StaticPage(
        title="Home",
        html='''
<div class="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 text-white">
  <div class="max-w-4xl mx-auto px-4 py-20 text-center">
    <h1 class="text-5xl font-black mb-4">Welcome to Xania</h1>
    <p class="text-xl text-slate-400 mb-8">A Python UI framework for building SPAs</p>
    <nav class="flex gap-4 justify-center">
      <a href="/" class="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition">Home</a>
      <a href="/about" class="px-6 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition">About</a>
    </nav>
  </div>
</div>
        '''
    )
)

app.route(
    "/about",
    StaticPage(
        title="About",
        html='''
<div class="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 text-white">
  <div class="max-w-4xl mx-auto px-4 py-20">
    <h1 class="text-5xl font-black mb-8">About</h1>
    <p class="text-lg text-slate-300 mb-4">This is a Xania website!</p>
    <p class="text-lg text-slate-300 mb-8">Edit this file and recompile to make changes.</p>
    <a href="/" class="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition">← Back to Home</a>
  </div>
</div>
        '''
    )
)

if __name__ == "__main__":
    from xania.runtime.compiler import SpaCompiler
    
    # Compile to static files in current directory
    compiler = SpaCompiler(title="My Website", tailwind=True)
    compiler.write(app, Path.cwd())
    print("✅ Website compiled! Run: xania serve .")
""", encoding="utf-8")
    
    # Create README
    readme = project_path / "README.md"
    readme.write_text(f"""# {project_name.title()}

A Xania website.

## Quick Start

1. **Compile your website:**
   ```bash
   python app.py
   ```
   This generates:
   - `index.html`
   - `static/app.js`
   - `static/spa_runtime.js`

2. **Run the server:**
   ```bash
   xania serve .
   ```
   
   Then open: http://127.0.0.1:8000

## Edit Your Site

- Edit `app.py` to add pages and change content
- Run `python app.py` to recompile
- Refresh browser to see changes

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
    click.echo("  python app.py          # Compile")
    click.echo("  xania serve .          # Run server")


@cli.command("dev")
@click.option("--app", "app_path", default=None, help="ASGI app path, e.g. module:app")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
@click.option("--reload/--no-reload", default=True, show_default=True)
def dev(app_path: Optional[str], host: str, port: int, reload: bool) -> None:
    """Run a development server (uvicorn --reload by default)."""
    cfg = CliConfig()
    _run_uvicorn(app_path or cfg.default_app, host=host, port=port, reload=reload)


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

