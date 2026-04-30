from __future__ import annotations

from renderer.elements import Element
from engine.serializer import serialize


def render(node: Element | str | None) -> str:
    """render(VDOM) -> HTML string."""
    return serialize(node)


__all__ = ["render"]

