from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class JsExpr:
    """
    Wrapper for raw JavaScript expressions (no quoting/escaping).
    Use sparingly: it bypasses safety.
    """

    code: str


class Page:
    """
    OOP unit of a SPA page.

    A page renders to a JS expression that evaluates to an HTML string.
    """

    def render_js(self, ctx_var: str) -> str:
        raise NotImplementedError


def _js_string(value: str) -> str:
    # Minimal JS string literal escaping.
    return (
        '"'
        + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        + '"'
    )


@dataclass(frozen=True)
class StaticPage(Page):
    title: str
    html: str

    def render_js(self, ctx_var: str) -> str:
        # Returns a JS string literal.
        return _js_string(self.html)


@dataclass(frozen=True)
class TemplatePage(Page):
    """
    HTML template with safe placeholder substitution.

    Placeholders are referenced as `{name}` and replaced by:
    - a JS-escaped string (default), or
    - raw JS expression when value is `JsExpr`.
    """

    title: str
    template: str
    placeholders: Mapping[str, str | JsExpr] = field(default_factory=dict)

    def render_js(self, ctx_var: str) -> str:
        # Convert `{name}` placeholders into JS concatenation segments.
        # This keeps the generated JS simple and debuggable.
        parts: list[str] = []
        text = self.template
        i = 0
        while True:
            start = text.find("{", i)
            if start == -1:
                tail = text[i:]
                if tail:
                    parts.append(_js_string(tail))
                break
            end = text.find("}", start + 1)
            if end == -1:
                raise ValueError("Unclosed placeholder in template")

            if start > i:
                parts.append(_js_string(text[i:start]))

            name = text[start + 1 : end].strip()
            if not name:
                raise ValueError("Empty placeholder in template")

            value = self.placeholders.get(name)
            if value is None:
                raise KeyError(f"Missing placeholder value: {name}")

            if isinstance(value, JsExpr):
                parts.append(f"({value.code})")
            else:
                # Ensure runtime escaping in case the string is user-controlled.
                # We rely on spa runtime's escapeHtml for safety.
                parts.append(f"{ctx_var}.escapeHtml({_js_string(value)})")

            i = end + 1

        return " + ".join(parts) if parts else _js_string("")


@dataclass(frozen=True)
class SpaRoute:
    path: str
    page: Page


@dataclass
class SpaApp:
    """
    High-level SPA spec in Python that can be compiled to JS.
    """

    name: str = "XaniaApp"
    root_id: str = "app"
    api_base: str = "/api"
    routes: list[SpaRoute] = field(default_factory=list)

    def route(self, path: str, page: Page) -> None:
        self.routes.append(SpaRoute(path=path, page=page))
