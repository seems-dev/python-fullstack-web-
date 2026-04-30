from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from renderer.component import Component


@dataclass(frozen=True)
class RuntimeConfig:
    title: str = "App"
    tailwind: bool = True


def html_shell(components: Iterable[tuple[str, Component]], config: RuntimeConfig | None = None) -> str:
    """
    Return a full HTML document with component mount points.

    - No inline JS.
    - The runtime is served from `/static/runtime.js`.
    - Each mount point is a single div with stable id + data-component name.
    """
    cfg = config or RuntimeConfig()

    mounts = "\n".join(
        f'    <div id="{c.id}" data-component="{name}"></div>' for name, c in components
    )

    tw = (
        '    <script src="https://cdn.tailwindcss.com"></script>\n'
        if cfg.tailwind
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{cfg.title}</title>
{tw}  </head>
  <body>
{mounts}
    <script src="/static/runtime.js"></script>
  </body>
</html>"""


__all__ = ["RuntimeConfig", "html_shell"]

