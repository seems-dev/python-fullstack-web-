"""
Xania Framework — Improved Patterns Guide

This file demonstrates the architectural improvements made to address
the feedback on the original design.
"""

# ─────────────────────────────────────────────────────────────────────
# PROBLEM 1: Placeholder System Fragility
# ─────────────────────────────────────────────────────────────────────

# BEFORE (Fragile {name} scanning):
# ────────────────────────────────
# from xania import TemplatePage, JsExpr
#
# page = TemplatePage(
#     title="User Profile",
#     template="<h1>{title}</h1><p>Email: {email}</p><p>Year: {year}</p>",
#     placeholders={
#         "title": "Welcome",
#         "email": "user@example.com",
#         "year": JsExpr("new Date().getFullYear()")
#     }
# )
# ISSUES:
# - Mixes Python and template syntax
# - String scanner is fragile (footgun: "NOTE: zero raw {} except...")
# - No IDE support or type safety
# - Unclear what's static vs. dynamic


# AFTER (Type-safe PageContext):
# ──────────────────────────────
from xania import TemplatePage, PageContext, JsExpr, StaticPage

# Pattern 1a: Function-based template (RECOMMENDED)
def user_profile_render(ctx: PageContext) -> str:
    """Explicit, IDE-friendly page rendering."""
    return f"""
    <div class="max-w-2xl">
        <h1>{ctx.title}</h1>
        <p>Email: {ctx.email}</p>
        <p>Year: {ctx.year}</p>
    </div>
    """

page = TemplatePage(
    title="User Profile",
    render_fn=user_profile_render
)

# Pattern 1b: Using Element builders with PageContext
from xania import Div, H1, P

def user_profile_elements(ctx: PageContext):
    """Build pages with type-safe elements."""
    return Div(
        H1(ctx.title),
        P("Email: ", ctx.email),
        # Static year, or use JsExpr for dynamic:
        P("Year: ", JsExpr("new Date().getFullYear()")),
        class_name="max-w-2xl"
    )

page = TemplatePage(
    title="User Profile",
    render_fn=user_profile_elements
)

# Benefits:
# ✓ No string scanning or escaping comments
# ✓ ctx.attribute is IDE-friendly and type-safe
# ✓ Explicit separation of static/dynamic content
# ✓ No mixing of template systems


# ─────────────────────────────────────────────────────────────────────
# PROBLEM 2: No Component Model
# ─────────────────────────────────────────────────────────────────────

# BEFORE (Functions returning strings):
# ────────────────────────────────────
# def nav_bar():
#     return '<nav><a href="/">Home</a></nav>'
#
# def section_label(title):
#     return f'<h2>{title}</h2>'
#
# ISSUES:
# - No lifecycle, no props validation
# - No composition pattern
# - Users invent inconsistent conventions
# - No metadata/introspection


# AFTER (Proper @component decorator):
# ─────────────────────────────────────
from xania import component, Div, H1, H2, A, Nav, Component, ComponentContext

@component(props={"items": list, "active": str})
def NavBar(ctx: ComponentContext):
    """
    Reusable navbar component with type-safe props.
    
    Args:
        items: List of (label, href) tuples
        active: Currently active page path
    """
    nav_items = []
    for label, href in ctx.props["items"]:
        is_active = href == ctx.props["active"]
        nav_items.append(
            A(label, href=href, class_name="nav-item" + (" active" if is_active else ""))
        )
    
    return Nav(*nav_items, class_name="flex gap-4 p-4")


@component(props={"title": str, "level": int})
def SectionLabel(ctx: ComponentContext):
    """Section heading with configurable level."""
    title = ctx.props["title"]
    level = ctx.props["level"]
    
    if level == 1:
        return H1(title)
    elif level == 2:
        return H2(title)
    # ... etc


# USAGE:
# ──────
navbar = NavBar(
    items=[("Home", "/"), ("About", "/about"), ("Contact", "/contact")],
    active="/"
)
print(navbar.to_html())  # Renders to HTML


section = SectionLabel(title="Getting Started", level=2)
print(section.to_html())


# Benefits:
# ✓ Props validation (type checking)
# ✓ Consistent interface across all components
# ✓ Metadata available for introspection
# ✓ Composable (nest components inside each other)
# ✓ Can extend with lifecycle hooks later


# ─────────────────────────────────────────────────────────────────────
# PROBLEM 3: app.py Scalability
# ─────────────────────────────────────────────────────────────────────

# BEFORE (All routes in one file):
# ──────────────────────────────
# # app.py - 2000+ lines
# from xania import SpaApp, StaticPage
#
# app = SpaApp()
# app.route("/", StaticPage(title="Home", html=...))
# app.route("/about", StaticPage(title="About", html=...))
# app.route("/blog/{id}", StaticPage(title="Post", html=...))
# # ... 100 more routes


# AFTER (Modular page organization):
# ───────────────────────────────────

# pages/home.py
def create_home_page():
    from xania import StaticPage, Div, H1, P
    return StaticPage(
        title="Home",
        html=str(Div(
            H1("Welcome to Xania"),
            P("A modern Python web framework"),
        ))
    )


# pages/blog.py
def create_blog_post_page(post_id: int):
    from xania import StaticPage, Div, H1, P, PageContext
    
    def render(ctx: PageContext):
        return Div(
            H1(f"Post {post_id}"),
            P(ctx.content),
        )
    
    from xania import TemplatePage
    return TemplatePage(title="Blog Post", render_fn=render)


# pages/__init__.py
from pages.home import create_home_page
from pages.blog import create_blog_post_page

def register_pages(app):
    """Auto-discovery pattern for organizing pages."""
    app.route("/", create_home_page())
    app.route("/blog/{id}", create_blog_post_page(id))


# app.py (now clean and minimal)
from xania import SpaApp
from pages import register_pages

app = SpaApp(name="MyApp")
register_pages(app)


# Benefits:
# ✓ Pages organized by feature (pages/, routes/)
# ✓ app.py remains small and clean
# ✓ Easy to test individual page modules
# ✓ Scales to 100+ routes without bloat


# ─────────────────────────────────────────────────────────────────────
# PROBLEM 4: Tailwind Underspecified
# ─────────────────────────────────────────────────────────────────────

# Current approach: Uses Tailwind CDN (documented below)

from xania import SpaCompiler

# The SpaCompiler with tailwind=True adds this to generated HTML:
#   <script src="https://cdn.tailwindcss.com"></script>
#
# This is explicit now. Future improvements:
# - Config option for custom CDN URL
# - Pre-built CSS option for offline usage
# - Tailwind CLI integration for production bundles

compiler = SpaCompiler(
    title="My App",
    tailwind=True  # Uses CDN, documented behavior
)

# For custom CSS:
# compiler = SpaCompiler(
#     title="My App",
#     tailwind=False,  # Disable CDN
#     css_path="/static/custom.css"  # Custom stylesheet
# )


# ─────────────────────────────────────────────────────────────────────
# PROBLEM 5: No Interactivity Story
# ─────────────────────────────────────────────────────────────────────

# CURRENT STATE (Static/Document Framework):
# ───────────────────────────────────────────
# Xania is intentionally designed as a static/document framework.
# It excels at:
# - Server-side rendered content
# - Static site generation
# - Multi-page SPA navigation
# - SEO-friendly content sites


# FUTURE: Progressive Enhancement
# ─────────────────────────────────
# When/if event handlers are added:
#
# @component()
# def Counter(ctx):
#     return Div(
#         P(ctx.props.get("count", 0)),
#         Button("+1", on_click=ctx.on_increment),
#     )
#
# This would be built on top of existing Component model.


print(__doc__)
