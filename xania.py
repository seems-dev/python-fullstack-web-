from __future__ import annotations

from pathlib import Path
import textwrap
import sys

import click


@click.group(invoke_without_command=True)
@click.option("--host", default="127.0.0.1", help="Host to bind when running the server")
@click.option("--port", default=8000, help="Port to bind when running the server")
@click.pass_context
def cli(ctx: click.Context, host: str, port: int) -> None:
    """Xania CLI — run, build and help for the Xania framework."""
    # If no subcommand was invoked, run the server by default.
    if ctx.invoked_subcommand is None:
        run_server(host, port)


@cli.command("run")
@click.option("--host", default="127.0.0.1", help="Host to bind")
@click.option("--port", default=8000, help="Port to bind")
def run(host: str, port: int) -> None:
    """Run the FastAPI app using uvicorn."""
    run_server(host, port)


def run_server(host: str, port: int) -> None:
    try:
        import uvicorn

        # Run the ASGI app from this package: `app:app`.
        uvicorn.run("app:app", host=host, port=int(port))
    except Exception as e:
        click.echo(f"Failed to start server: {e}")
        sys.exit(1)


@cli.command("build")
@click.option("--out", default="index.html", help="Output filename (in CWD)")
def build(out: str) -> None:
    """Generate static HTML files in the current working directory.

    This will render all registered components and write a single HTML file.
    """
    try:
        from xania.renderer.registry import ComponentRegistry
        from xania.engine.runtime import RuntimeConfig

        components = ComponentRegistry.all()

        mounts_lines = []
        for name, comp in components.items():
            html = comp.to_html()
            mounts_lines.append(f'    <div id="{comp.id}" data-component="{name}">')
            mounts_lines.append(html)
            mounts_lines.append("    </div>")

        tw = '    <script src="https://cdn.tailwindcss.com"></script>\n' if RuntimeConfig().tailwind else ""

        html_doc = textwrap.dedent(f"""\
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{RuntimeConfig().title}</title>
{tw}  </head>
          <body>
{chr(10).join(mounts_lines)}
            <script>window.XaniaConfig={{serverEvents:true}};</script>
            <script src="/static/runtime.js?v=2"></script>
          </body>
        </html>
        """)

        out_path = Path.cwd() / out
        out_path.write_text(html_doc, encoding="utf-8")
        click.echo(f"Wrote static HTML to {out_path}")
    except Exception as e:
        click.echo(f"Build failed: {e}")
        sys.exit(1)


@cli.command("help")
def help_cmd() -> None:
    """Show a step-by-step tutorial for using Xania to create a website."""
    tutorial = """
    Step-by-step Xania tutorial

    1) Create components in `example/` by subclassing `renderer.component.Component`.
       Implement `render()` and optional `on_<action>()` handlers.

    2) Register components in `app.py` using `ComponentRegistry.register("Name", YourComponent(id="your-id"))`.

    3) During development run the server:
       $ python xania.py run --host 0.0.0.0 --port 8000

    4) To generate static files suitable for deployment (writes `index.html` by default):
       $ python xania.py build --out index.html

    5) Serve the generated `index.html` and the `static/` folder from any static host.

    6) For API interactions the runtime expects `/event` POST endpoint handled by the app.

    That's it — build components, register them, run locally, or `build` for static output.
    """
    click.echo(tutorial)


if __name__ == "__main__":
    cli()
