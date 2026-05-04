from __future__ import annotations

from html import escape
from typing import Any

from xania.renderer.elements import Element, VoidElement


def _escape_attr(value: Any) -> str:
    # Escape for HTML attributes surrounded with double quotes.
    return escape(str(value), quote=True)


def _normalize_attr_name(name: str) -> str:
    if name == "class_name":
        return "class"
    if name == "for_":
        return "for"
    if name == "http_equiv":
        return "http-equiv"
    return name.replace("_", "-")


def serialize(node: Element | str | None) -> str:
    """
    Convert VDOM nodes into HTML.

    - Escapes text nodes
    - Escapes attribute values
    - Normalizes python-friendly attribute names (class_name -> class, etc.)
    """
    if node is None:
        return ""

    if isinstance(node, str):
        return escape(node)

    if isinstance(node, VoidElement):
        attrs = _serialize_attrs(node.attrs)
        return f"<{node.tag}{attrs} />"

    attrs = _serialize_attrs(node.attrs)
    children_html = "".join(serialize(c if isinstance(c, (Element, str)) else str(c)) for c in node.children if c is not None)
    return f"<{node.tag}{attrs}>{children_html}</{node.tag}>"


def _serialize_attrs(attrs: dict[str, Any]) -> str:
    parts: list[str] = []
    for k, v in attrs.items():
        name = _normalize_attr_name(k)
        if v is None or v is False:
            continue
        if v is True:
            parts.append(name)
            continue
        parts.append(f'{name}="{_escape_attr(v)}"')
    return (" " + " ".join(parts)) if parts else ""


__all__ = ["serialize"]
