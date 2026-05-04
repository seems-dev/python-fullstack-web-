from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional


@dataclass(frozen=True)
class JsExpr:
    """
    Wrapper for raw JavaScript expressions (no quoting/escaping).
    Use sparingly: it bypasses safety.
    """

    code: str


@dataclass
class PageContext:
    """
    Type-safe context object for template rendering.
    
    Replaces the fragile {name} placeholder scanner.
    All page data is stored as attributes, making it explicit and IDE-friendly.
    
    Example:
        ctx = PageContext(email="user@example.com", year=2026)
        # Access: ctx.email, ctx.year
    """

    def __init__(self, **kwargs: Any):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> dict[str, Any]:
        """Export context as a dictionary for serialization."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


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
    
    Two usage patterns:
    
    1. Function-based (RECOMMENDED):
        def render(ctx):
            return f'<h1>{ctx.title}</h1>'
        
        page = TemplatePage(title="Home", render_fn=render)
    
    2. String-based (DEPRECATED, use for backwards compatibility):
        page = TemplatePage(
            title="Home",
            template="{title}",
            placeholders={"title": "Welcome"}
        )
    
    The function approach is preferred because it's type-safe and IDE-friendly.
    """

    title: str
    render_fn: Optional[Callable[[PageContext], str | JsExpr]] = field(default=None)
    
    # Legacy fields (kept for backwards compatibility)
    template: Optional[str] = field(default=None)
    placeholders: Mapping[str, str | JsExpr] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.render_fn is None and self.template is None:
            raise ValueError("TemplatePage requires either render_fn or template")

    def render_js(self, ctx_var: str) -> str:
        if self.render_fn is not None:
            # New function-based approach
            # Note: render_fn would need access to actual context at runtime
            # For now, return a placeholder that indicates this is a dynamic page
            return f"(() => {{ /* page={self.title} */ return 'rendered'; }})()"
        else:
            # Legacy {name} placeholder scanning
            return self._render_legacy(ctx_var)

    def _render_legacy(self, ctx_var: str) -> str:
        """Legacy placeholder rendering for backwards compatibility."""
        parts: list[str] = []
        text = self.template or ""
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
    
    Recommended usage for scalable apps:
    1. Keep routes in separate page modules (pages/home.py, pages/about.py)
    2. Create a pages/__init__.py that imports and registers all pages
    3. Call register_pages(app) in your main app.py
    
    Example:
        # pages/home.py
        def create_home():
            return StaticPage(title="Home", html="...")
        
        # pages/__init__.py
        def register_pages(app):
            app.route("/", create_home())
        
        # app.py
        from pages import register_pages
        app = SpaApp()
        register_pages(app)
    """

    name: str = "XaniaApp"
    root_id: str = "app"
    api_base: str = "/api"
    routes: list[SpaRoute] = field(default_factory=list)

    def route(self, path: str, page: Page) -> None:
        """Register a route with its page."""
        self.routes.append(SpaRoute(path=path, page=page))
    
    def find_route(self, path: str) -> Optional[SpaRoute]:
        """Find a route by path (useful for testing)."""
        for route in self.routes:
            if route.path == path:
                return route
        return None
    
    def route_count(self) -> int:
        """Get the number of registered routes."""
        return len(self.routes)
