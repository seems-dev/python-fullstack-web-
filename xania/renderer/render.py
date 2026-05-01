from __future__ import annotations

from xania.engine.serializer import serialize
from xania.renderer.elements import Element


def render(node: Element | str | None) -> str:
    """render(VDOM) -> HTML string."""
    return serialize(node)


__all__ = ["render"]
